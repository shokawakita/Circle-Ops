#!/usr/bin/env python3
"""つなげーと連携のコマンド。

  python3 scripts/tunagate/cli.py check   --body-file <md> --event-date <ISO>
  python3 scripts/tunagate/cli.py create  --body-file <md> --event-date <ISO> [--dry-run]
  python3 scripts/tunagate/cli.py drafts
  python3 scripts/tunagate/cli.py publish --id <id>

check と create --dry-run はトークン不要（ネットワークに出ない。画像確認を除く）。
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import checks  # noqa: E402
import client  # noqa: E402
import overview  # noqa: E402


def _load_dotenv() -> None:
    """リポジトリ直下の .env を読む（あれば）。既存の環境変数は上書きしない。"""
    env = pathlib.Path(__file__).resolve().parents[2] / ".env"
    if not env.exists():
        return
    for line in env.read_text("utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _report(result: checks.Result) -> None:
    for w in result.warnings:
        print(f"  [注意] {w}")
    for e in result.errors:
        print(f"  [中止] {e}")


def _parse_body(path: str) -> overview.Overview:
    return overview.parse(pathlib.Path(path).read_text("utf-8"))


def cmd_check(args) -> int:
    ov = _parse_body(args.body_file)
    draft_count = None
    if args.with_draft_count:
        _load_dotenv()
        draft_count = client.count_drafts(client.Tunagate())

    result = checks.run(ov, draft_count=draft_count, check_image=not args.skip_image)

    print(f"募集タイトル: {ov.title or '(なし)'}")
    print(f"定員        : {ov.capacity if ov.capacity is not None else '(なし)'}")
    print(f"チケット    : {len(ov.plans)} 件")
    for p in ov.plans:
        limit = f" / 期限 {p.expired_at}" if p.expired_at else ""
        print(f"  - {p.name}: {p.price}円 / {p.capacity}名{limit}")
    if draft_count is not None:
        print(f"下書き      : {draft_count} / {checks.DRAFT_LIMIT} 件")

    _report(result)
    if result.ok:
        print("\nチェックを通過しました。")
        return 0
    print(f"\n{len(result.errors)} 件の問題があるため、つなげーとには作成しません。")
    return 1


def cmd_create(args) -> int:
    _load_dotenv()
    ov = _parse_body(args.body_file)

    draft_count = None
    if not args.dry_run:
        draft_count = client.count_drafts(client.Tunagate())

    result = checks.run(ov, draft_count=draft_count, check_image=not args.skip_image)
    if not result.ok:
        _report(result)
        print(f"\n{len(result.errors)} 件の問題があるため作成を中止しました。")
        return 1
    for w in result.warnings:
        print(f"  [注意] {w}")

    circle_id = os.environ.get("TUNAGATE_CIRCLE_ID", "")
    params = client.build_params(ov, args.event_date, circle_id=circle_id)

    if args.dry_run:
        print("--- 送信するパラメータ（dry-run。実際には送りません） ---")
        for key, value in params:
            shown = value if len(value) <= 120 else value[:117] + "..."
            print(f"{key} = {shown}")
        return 0

    response = client.Tunagate().create_draft(params)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    print("\n下書きを作成しました。公開はしていません。")
    print("つなげーとの編集画面で内容を確認してから、公開ボタンを押してください。")
    return 0


def cmd_drafts(args) -> int:
    _load_dotenv()
    c = client.Tunagate()
    print(f"下書き: {client.count_drafts(c)} / {checks.DRAFT_LIMIT} 件")
    return 0


def cmd_publish(args) -> int:
    _load_dotenv()
    print(json.dumps(client.Tunagate().publish(args.id), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="つなげーと連携")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_body_args(p):
        p.add_argument("--body-file", required=True, help="Notion ページ本文の Markdown")
        p.add_argument("--skip-image", action="store_true", help="画像URLの到達確認を省く")

    p_check = sub.add_parser("check", help="投稿前のチェックだけを行う")
    add_body_args(p_check)
    p_check.add_argument("--event-date", help="開催日時（表示用）")
    p_check.add_argument("--with-draft-count", action="store_true", help="下書き数も数える")
    p_check.set_defaults(func=cmd_check)

    p_create = sub.add_parser("create", help="チェックを通れば下書きを作成する")
    add_body_args(p_create)
    p_create.add_argument("--event-date", required=True, help="開催日時 ISO 8601")
    p_create.add_argument("--dry-run", action="store_true", help="送信せずパラメータだけ出す")
    p_create.set_defaults(func=cmd_create)

    p_drafts = sub.add_parser("drafts", help="下書きの残り枠を数える")
    p_drafts.set_defaults(func=cmd_drafts)

    p_publish = sub.add_parser("publish", help="公開する（人の確認後にのみ使う）")
    p_publish.add_argument("--id", required=True)
    p_publish.set_defaults(func=cmd_publish)

    args = parser.parse_args()
    try:
        return args.func(args)
    except client.TunagateError as e:
        print(f"つなげーとAPIエラー: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
