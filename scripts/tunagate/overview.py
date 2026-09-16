"""Notion ページ本文から「イベント概要」と「募集本文」を読み取る。

書式は docs/notion-event-rules.md を参照。
【】 で囲んだキーワードを目印にしているため、表記ゆれで壊れない。
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


KEY_TITLE = "【募集タイトル】"
KEY_IMAGE = "【メイン画像】"
KEY_CAPACITY = "【定員】"
KEY_PRICE = "【参加費】"
KEY_PLACE = "【場所】"
KEY_PLACE_DETAIL = "【会場詳細】"
KEY_PREFECTURE = "【都道府県】"
KEY_MIN_PEOPLE = "【最小催行人数】"
KEY_APPLICATION_DUE = "【申込締切】"

HEADING_OVERVIEW = "イベント概要"
HEADING_BODY = "募集本文"


@dataclass
class Plan:
    """参加費テーブルの1行＝つなげーとのプラン1件。"""

    name: str
    price: int
    capacity: int | None = None
    expired_at: str | None = None


@dataclass
class Overview:
    title: str | None = None
    image_url: str | None = None
    capacity: int | None = None
    place: str | None = None
    place_detail: str | None = None
    prefecture: str | None = None
    min_num_of_people: int | None = None
    application_due_date: str | None = None
    plans: list[Plan] = field(default_factory=list)
    body: str | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _is_todo(value: str) -> bool:
    """未記入の目印。TODO: が残った値は「埋めた体で進めない」（CLAUDE.md）。"""
    return _normalize(value).strip().upper().startswith("TODO")


def _normalize(text: str) -> str:
    """全角数字・全角英字を半角に寄せる。全角の【】と日本語は保つ。"""
    return unicodedata.normalize("NFKC", text)


def _to_int(raw: str, label: str, errors: list[str]) -> int | None:
    """「2,500円」「12名」のような表記から数値だけを取り出す。"""
    cleaned = _normalize(raw).strip()
    cleaned = re.sub(r"[,\s]", "", cleaned)
    cleaned = re.sub(r"(円|名|人|枚)$", "", cleaned)
    if not cleaned:
        return None
    if not re.fullmatch(r"-?\d+", cleaned):
        errors.append(f"{label} が数値として読めません: {raw!r}")
        return None
    return int(cleaned)


def _to_datetime(raw: str, label: str, errors: list[str]) -> str | None:
    """「2026-10-05 23:59」を ISO 8601 に直す。空欄は無期限扱い。"""
    cleaned = _normalize(raw).strip()
    if not cleaned:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?", cleaned)
    if not m:
        errors.append(f"{label} は YYYY-MM-DD HH:MM の形式で書いてください: {raw!r}")
        return None
    y, mo, d, h, mi, sec = m.groups()
    return f"{y}-{mo}-{d}T{h}:{mi}:{sec or '00'}"


def _section(markdown: str, heading: str, *, to_end: bool = False) -> str | None:
    """`## 見出し` 以下を切り出す。

    to_end=False なら次の見出しの手前まで。
    to_end=True なら本文の最後まで。募集本文は「当日の流れ」「お願い」
    「キャンセルについて」といった見出しを内側に持つため、こちらを使う。
    """
    pattern = re.compile(
        r"^#{1,6}\s*" + re.escape(heading) + r"\s*$", re.MULTILINE
    )
    m = pattern.search(markdown)
    if not m:
        return None
    start = m.end()
    if to_end:
        return markdown[start:].strip()
    nxt = re.compile(r"^#{1,6}\s+\S", re.MULTILINE).search(markdown, start)
    return markdown[start : nxt.start() if nxt else len(markdown)].strip()


def _inline_value(text: str, key: str) -> str | None:
    """`【定員】12` の値部分を返す。同じキーが複数あれば最初の1つ。"""
    for line in text.splitlines():
        stripped = line.strip().lstrip("-*+ \t").strip()
        if stripped.startswith(key):
            return stripped[len(key) :].strip()
    return None


def _parse_table(text: str, errors: list[str]) -> list[Plan]:
    """【参加費】直後の Markdown テーブルを読む。"""
    lines = text.splitlines()
    start = next(
        (i for i, ln in enumerate(lines) if ln.strip().startswith(KEY_PRICE)), None
    )
    if start is None:
        errors.append(
            f"{KEY_PRICE} がありません。プランを省略するとつなげーと側で"
            "無料プラン1件が自動生成されるため、有料の回が無料で公開されます"
        )
        return []

    rows: list[list[str]] = []
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if not stripped:
            if rows:
                break
            continue
        if not stripped.startswith("|"):
            break
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue  # 区切り行
        rows.append(cells)

    if len(rows) < 2:
        errors.append(
            f"{KEY_PRICE} の直後にチケットの表が見つかりません。"
            "行が1つでも表で書いてください"
        )
        return []

    header = [_normalize(c) for c in rows[0]]
    try:
        i_name = header.index("チケット名")
        i_price = header.index("価格")
    except ValueError:
        errors.append(
            f"{KEY_PRICE} の表に「チケット名」「価格」の列が必要です。"
            f"いまの見出し: {rows[0]}"
        )
        return []
    i_cap = header.index("定員") if "定員" in header else None
    i_exp = header.index("販売期限") if "販売期限" in header else None

    plans: list[Plan] = []
    for cells in rows[1:]:
        if len(cells) <= max(i_name, i_price):
            continue
        name = cells[i_name].strip()
        if not name:
            continue
        if _is_todo(name):
            errors.append(f"{KEY_PRICE} の表に TODO: のままの行があります")
            continue
        price = _to_int(cells[i_price], f"チケット「{name}」の価格", errors)
        if price is None:
            continue
        capacity = (
            _to_int(cells[i_cap], f"チケット「{name}」の定員", errors)
            if i_cap is not None and i_cap < len(cells)
            else None
        )
        expired_at = (
            _to_datetime(cells[i_exp], f"チケット「{name}」の販売期限", errors)
            if i_exp is not None and i_exp < len(cells)
            else None
        )
        plans.append(Plan(name=name, price=price, capacity=capacity, expired_at=expired_at))

    if not plans:
        errors.append(f"{KEY_PRICE} の表に読み取れる行がありません")
    return plans


def parse(markdown: str) -> Overview:
    """ページ本文を読んで Overview を返す。足りないものは errors に入る。"""
    result = Overview()

    overview = _section(markdown, HEADING_OVERVIEW)
    if overview is None:
        result.errors.append(f"「## {HEADING_OVERVIEW}」の見出しが見つかりません")
        return result

    title = _inline_value(overview, KEY_TITLE)
    if not title:
        result.errors.append(f"{KEY_TITLE} がありません。推測では埋めません")
    elif _is_todo(title):
        result.errors.append(f"{KEY_TITLE} が TODO: のままです")
    else:
        result.title = title

    image = _inline_value(overview, KEY_IMAGE)
    if image and _is_todo(image):
        result.errors.append(f"{KEY_IMAGE} が TODO: のままです。不要なら行ごと消してください")
    elif image:
        if not image.startswith("https://"):
            result.errors.append(f"{KEY_IMAGE} は https:// で始まるURLにしてください: {image!r}")
        elif "prod-files-secure.s3" in image or "X-Amz-Signature" in image:
            result.errors.append(
                f"{KEY_IMAGE} が Notion 添付の署名付きURLです。数分で失効するため使えません"
            )
        else:
            result.image_url = image

    capacity_raw = _inline_value(overview, KEY_CAPACITY)
    if capacity_raw is None:
        result.errors.append(f"{KEY_CAPACITY} がありません")
    elif _is_todo(capacity_raw):
        result.errors.append(f"{KEY_CAPACITY} が TODO: のままです")
    else:
        result.capacity = _to_int(capacity_raw, KEY_CAPACITY, result.errors)

    # 以下は任意項目。未検証フィールドのため、省略してもエラーにしない（docs/tunagate-api.md 参照）
    place = _inline_value(overview, KEY_PLACE)
    if place and not _is_todo(place):
        result.place = place

    place_detail = _inline_value(overview, KEY_PLACE_DETAIL)
    if place_detail and not _is_todo(place_detail):
        result.place_detail = place_detail

    prefecture = _inline_value(overview, KEY_PREFECTURE)
    if prefecture and not _is_todo(prefecture):
        result.prefecture = prefecture

    min_people_raw = _inline_value(overview, KEY_MIN_PEOPLE)
    if min_people_raw and not _is_todo(min_people_raw):
        result.min_num_of_people = _to_int(min_people_raw, KEY_MIN_PEOPLE, result.errors)

    due_raw = _inline_value(overview, KEY_APPLICATION_DUE)
    if due_raw and not _is_todo(due_raw):
        result.application_due_date = _to_datetime(due_raw, KEY_APPLICATION_DUE, result.errors)

    result.plans = _parse_table(overview, result.errors)

    body = _section(markdown, HEADING_BODY, to_end=True)
    if body:
        result.body = body
    else:
        result.errors.append(f"「## {HEADING_BODY}」の見出しが見つかりません")

    return result
