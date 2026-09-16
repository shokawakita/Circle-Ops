# scripts/tunagate

つなげーと 外部API との連携。標準ライブラリだけで動きます（追加インストール不要）。

API仕様は `docs/tunagate-api.md`、Notion 側の書式は `docs/notion-event-rules.md`。

## 準備

```bash
cp .env.example .env
# .env に TUNAGATE_API_TOKEN を書く（.gitignore 済み）
```

## 使い方

```bash
# 投稿前チェックだけ（ネットワークに出ない。--with-draft-count を付けるとAPIを見る）
python3 scripts/tunagate/cli.py check --body-file <ページ本文.md> --with-draft-count

# 送信せずパラメータだけ確認
python3 scripts/tunagate/cli.py create --body-file <md> --event-date 2026-10-12T14:00:00 --dry-run

# チェックを通れば下書きを作成（公開はしない）
python3 scripts/tunagate/cli.py create --body-file <md> --event-date 2026-10-12T14:00:00

# 下書きの残り枠
python3 scripts/tunagate/cli.py drafts

# 公開（人が内容を確認したあとにのみ）
python3 scripts/tunagate/cli.py publish --id 456
```

`create` は**下書きまで**です。公開は `publish` を明示的に呼んだときだけ行われます。

## ファイル

| ファイル | 役割 |
|---|---|
| `overview.py` | ページ本文の `## イベント概要` / `## 募集本文` を読む |
| `checks.py` | 投稿前のチェック（下書き枠・プラン有無・画像到達・定員一致・NG語・規約） |
| `client.py` | API呼び出しとペイロード組み立て |
| `field_map.json` | APIパラメータ名の対応表。仕様が変わったらここだけ直す |
| `cli.py` | コマンド |

## テスト

```bash
python3 -m unittest discover -s tests
```

## 未検証の箇所

`events_plans[][...]` の中のキー名（`name` / `price` / `capacity`）は、
公式ドキュメントに `expired_at` しか記載がないため**推定です**。

最初の1回は必ず `--dry-run` で送信内容を確認し、実際に作成したあとに
つなげーとの編集画面でチケットが意図どおり入っているかを見てください。
違っていれば `field_map.json` だけ直せば済みます。
