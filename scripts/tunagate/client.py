"""つなげーと 外部API の薄いラッパ。

仕様は docs/tunagate-api.md を参照。標準ライブラリのみで動く。
"""

from __future__ import annotations

import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://tunagate.com/api/external"
FIELD_MAP = json.loads((pathlib.Path(__file__).with_name("field_map.json")).read_text("utf-8"))

PAGE_SIZE = 50  # 一覧は1ページ50件固定

# 都道府県名 → pref_id。JIS X 0401 の都道府県コードを仮定している。
# 実データで確認できたのは 13（東京都）のみ。他の値は未検証。
# サークルの活動エリア（神奈川・東京）に絞って必要な分だけ持つ（docs/tunagate-api.md 参照）。
PREFECTURE_IDS = {
    "東京都": 13,
    "神奈川県": 14,
}


class TunagateError(RuntimeError):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"[{status}] {message}")


def _explain(status: int, message: str) -> str:
    hints = {
        401: "トークンが無効・失効・期限切れです。.env の TUNAGATE_API_TOKEN を確認してください",
        404: "権限が無いか、対象が存在しません（APIはこの2つを区別しません）",
        # 2026-09-25: 下書き上限（10件）は運営側で撤廃済み（docs/tunagate-api.md 参照）。
        # 古いヒントを出し続けないよう更新。
        422: "入力エラー、または公開条件未達です",
    }
    hint = hints.get(status)
    return f"{message}（{hint}）" if hint else message


class Tunagate:
    def __init__(self, token: str | None = None, circle_id: str | None = None):
        self.token = token or os.environ.get("TUNAGATE_API_TOKEN", "")
        self.circle_id = circle_id or os.environ.get("TUNAGATE_CIRCLE_ID", "")
        if not self.token:
            raise RuntimeError(
                "TUNAGATE_API_TOKEN が設定されていません。.env.example を参考に .env を作ってください"
            )

    # ---- HTTP ----------------------------------------------------------

    def _request(self, method: str, path: str, params: list[tuple[str, str]] | None = None):
        url = f"{BASE_URL}{path}"
        data = None
        if method in ("POST", "PATCH") and params:
            data = urllib.parse.urlencode(params).encode("utf-8")
        elif method == "GET" and params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        if data:
            req.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                raw = res.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                message = json.loads(raw).get("error", raw)
            except json.JSONDecodeError:
                message = raw
            raise TunagateError(e.code, _explain(e.code, message)) from None

        return json.loads(raw) if raw.strip() else {}

    # ---- エンドポイント -------------------------------------------------

    def list_events(self, page: int = 1, *, include_drafts: bool = False):
        params = [("circle_id", self.circle_id), ("page", str(page))]
        if include_drafts:
            # 2026-09-25判明: これを付けないと下書きが1件も返らない（docs/tunagate-api.md）。
            params.append(("include_drafts", "true"))
        return self._request("GET", "/events", params)

    def get_event(self, event_id: str | int):
        return self._request("GET", f"/events/{event_id}")

    def create_draft(self, params: list[tuple[str, str]]):
        return self._request("POST", "/events", params)

    def update(self, event_id: str | int, params: list[tuple[str, str]]):
        return self._request("PATCH", f"/events/{event_id}", params)

    def publish(self, event_id: str | int):
        return self._request("POST", f"/events/{event_id}/publish")


# ---- ペイロード組み立て ------------------------------------------------


def _events(payload) -> list:
    """一覧レスポンスの形が配列でも {events: [...]} でも拾えるようにする。"""
    if isinstance(payload, list):
        return payload
    for key in ("events", "data", "items", "results"):
        if isinstance(payload.get(key), list):
            return payload[key]
    return []


def count_drafts(client: Tunagate) -> int:
    """下書きの件数を数える。

    2026-09-25判明: 下書き上限（10件）自体は運営側で撤廃済みなので、この関数は
    もう作成の可否を左右しない。不要な下書きを掃除する判断材料として残している。
    `include_drafts=true` を付けないと一覧に下書きが1件も含まれない
    （docs/tunagate-api.md 参照）。
    """
    total = 0
    page = 1
    while True:
        events = _events(client.list_events(page=page, include_drafts=True))
        for ev in events:
            status = str(ev.get("status") or ev.get("state") or "").lower()
            published = ev.get("published_at") or ev.get("published")
            if status == "draft" or (not status and not published):
                total += 1
        if len(events) < PAGE_SIZE:
            return total
        page += 1


def build_params(
    ov,
    event_date: str,
    circle_id: str | None = None,
    event_end_date: str | None = None,
) -> list[tuple[str, str]]:
    """Overview からフォームエンコード用のパラメータ列を作る。

    events_plans[] は「1件分のキーをまとめて並べる」順序で出す。
    途中で順序を崩すとプランの対応が壊れる。

    capacity / place / place_detail / pref_id / min_num_of_people /
    application_due_date / event_end_datetime は 2026-09-16 に追加した
    未検証フィールド（field_map.json の _unverified_fields）。
    キー名が違っていた場合は反映されないだけで、他のフィールドには影響しない想定。
    """
    fm = FIELD_MAP
    uf = fm["_unverified_fields"]
    params: list[tuple[str, str]] = []
    if circle_id:
        params.append((fm["circle_id"], str(circle_id)))
    params.append((fm["title"], ov.title or ""))
    params.append((fm["event_date"], event_date))
    if event_end_date:
        params.append((uf["event_end_datetime"], event_end_date))
    if ov.body:
        params.append((fm["body"], ov.body))
    if ov.image_url:
        params.append((fm["main_image_url"], ov.image_url))
    if ov.capacity is not None:
        params.append((uf["capacity"], str(ov.capacity)))
    if ov.place:
        params.append((uf["place"], ov.place))
    if ov.place_detail:
        params.append((uf["place_detail"], ov.place_detail))
    if ov.prefecture:
        pref_id = PREFECTURE_IDS.get(ov.prefecture)
        if pref_id is not None:
            params.append((uf["pref_id"], str(pref_id)))
    if ov.min_num_of_people is not None:
        params.append((uf["min_num_of_people"], str(ov.min_num_of_people)))
    if ov.application_due_date:
        params.append((uf["application_due_date"], ov.application_due_date))

    plan_keys = fm["plan"]
    for plan in ov.plans:
        params.append((plan_keys["name"], plan.name))
        params.append((plan_keys["price"], str(plan.price)))
        if plan.capacity is not None:
            params.append((plan_keys["capacity"], str(plan.capacity)))
        if plan.expired_at:
            params.append((plan_keys["expired_at"], plan.expired_at))
    return params
