"""つなげーとに投げる前の機械的なチェック。

1つでも引っかかったら作成せずに止める。
判断が要るもの（企画の中身、トンマナの良し悪し）は人と Claude が見る。
"""

from __future__ import annotations

import re
import urllib.error
import urllib.request
from dataclasses import dataclass

DRAFT_LIMIT = 10

# brand/voice.md の「使わない言葉」より
NG_WORDS = ["恋活", "婚活", "出会い", "絶対に", "必ず", "100%", "ハイスペック"]

# 飲酒を伴う回の判定に使う語
ALCOHOL_WORDS = ["日本酒", "ビール", "ワイン", "居酒屋", "飲み放題", "お酒", "酒場"]


@dataclass
class Result:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def image_reachable(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    """main_image_url の取得に失敗するとリクエスト全体が 422 になるため事前に見る。"""
    req = urllib.request.Request(url, method="GET", headers={"Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            code = res.status
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:  # ネットワーク到達不可も含めてまとめて扱う
        return False, str(e)
    return (200 <= code < 400), f"HTTP {code}"


def run(
    ov,
    *,
    draft_count: int | None = None,
    check_image: bool = True,
) -> Result:
    """Overview を受け取り、止めるべき理由を集める。"""
    errors: list[str] = list(ov.errors)
    warnings: list[str] = []

    if draft_count is not None and draft_count >= DRAFT_LIMIT:
        errors.append(
            f"下書きが {draft_count} 件あり、上限 {DRAFT_LIMIT} 件に達しています。"
            "不要な下書きを消してから作成してください（超えると 422）"
        )

    if not ov.plans:
        pass  # ov.errors 側で報告済み
    else:
        total = sum(p.capacity for p in ov.plans if p.capacity is not None)
        if ov.capacity is not None and total and total != ov.capacity:
            # 2026-09-16: 実データ（594081）で全体定員20名・チケット定員合計26名という
            # 一致しない例を確認済み。早割系チケットが埋まると閉じる設計のため、
            # 合計が全体定員を上回ること自体は正常。止めずに注意のみ表示する。
            warnings.append(
                f"チケット定員の合計 {total} 名が【定員】{ov.capacity} 名と一致しません"
                "（早割チケットの重複販売などで一致しないのは正常な場合があります）"
            )
        if any(p.price == 0 for p in ov.plans) and any(p.price > 0 for p in ov.plans):
            warnings.append("無料のチケットと有料のチケットが混在しています")

    if ov.prefecture and ov.prefecture not in ("東京都", "神奈川県"):
        warnings.append(
            f"【都道府県】「{ov.prefecture}」は pref_id の対応表（client.PREFECTURE_IDS）に無く、"
            "pref_id は送信されません"
        )

    if ov.image_url and check_image:
        ok, detail = image_reachable(ov.image_url)
        if not ok:
            errors.append(
                f"【メイン画像】に到達できません（{detail}）。"
                "取得に失敗するとリクエスト全体が 422 で落ちます"
            )

    body = ov.body or ""
    if body:
        for word in NG_WORDS:
            if word in body:
                errors.append(f"募集本文に brand/voice.md の使わない言葉があります: 「{word}」")

        if "キャンセル" not in body:
            errors.append("募集本文にキャンセルポリシーがありません（brand/rules.md）")

        # 2026-09-26: 対象年齢はつなげーと側の設定（申込時のチェック）で管理するため、
        # 募集本文への記載は不要になった（運営確認済み）。本文チェックの対象からは外すが、
        # 飲酒を伴う回で20歳未満を対象にしてしまわないよう、本文に年齢の記載がある場合だけ
        # 矛盾を警告する。
        if re.search(r"\d{2}\s*歳", body) and any(w in body for w in ALCOHOL_WORDS) and "20歳" not in _normalize_age(body):
            warnings.append("飲酒を伴う回は対象を20歳以上にしてください（brand/rules.md）")

        if "勧誘" not in body:
            warnings.append("募集本文に勧誘禁止の記載が見当たりません（brand/rules.md）")

    return Result(errors=errors, warnings=warnings)


def _normalize_age(body: str) -> str:
    return body.replace(" ", "").replace("　", "")
