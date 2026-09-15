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


class TunagateError(RuntimeError):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"[{status}] {message}")


def _explain(status: int, message: str) -> str:
    hints = {
        401: "トークンが無効・失効・期限切れです。.env の TUNAGATE_API_TOKEN を確認してください",
        404: "権限が無いか、対象が存在しません（APIはこの2つを区別しません）",
        422: "入力エラー、下書き上限（10件）超過、または公開条件未達です",
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

    def list_events(self, page: int = 1):
        return self._request(
            "GET", "/events", [("circle_id", self.circle_id), ("page", str(page))]
        )

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
    """下書きの件数を数える。上限10件に達していると新規作成が 422 で落ちるため。"""
    total = 0
    page = 1
    while True:
        events = _events(client.list_events(page=page))
        for ev in events:
            status = str(ev.get("status") or ev.get("state") or "").lower()
            published = ev.get("published_at") or ev.get("published")
            if status == "draft" or (not status and not published):
                total += 1
        if len(events) < PAGE_SIZE:
            return total
        page += 1


def build_params(ov, event_date: str, circle_id: str | None = None) -> list[tuple[str, str]]:
    """Overview からフォームエンコード用のパラメータ列を作る。

    events_plans[] は「1件分のキーをまとめて並べる」順序で出す。
    途中で順序を崩すとプランの対応が壊れる。
    """
    fm = FIELD_MAP
    params: list[tuple[str, str]] = []
    if circle_id:
        params.append((fm["circle_id"], str(circle_id)))
    params.append((fm["title"], ov.title or ""))
    params.append((fm["event_date"], event_date))
    if ov.body:
        params.append((fm["body"], ov.body))
    if ov.image_url:
        params.append((fm["main_image_url"], ov.image_url))

    plan_keys = fm["plan"]
    for plan in ov.plans:
        params.append((plan_keys["name"], plan.name))
        params.append((plan_keys["price"], str(plan.price)))
        if plan.capacity is not None:
            params.append((plan_keys["capacity"], str(plan.capacity)))
        if plan.expired_at:
            params.append((plan_keys["expired_at"], plan.expired_at))
    return params
