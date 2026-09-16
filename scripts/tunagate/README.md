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

# 下書きの残り枠（※ 下記「未検証の箇所」参照。過小報告する可能性あり）
python3 scripts/tunagate/cli.py drafts

# 既存イベントの詳細を取得（読み取りのみ。Notion本文が空でもつなげーと側の実データを確認できる）
python3 scripts/tunagate/cli.py show --id 594081

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

### `drafts` コマンドは下書き数を過小報告する可能性がある（2026-09-16 発見）

`GET /api/external/events` の一覧レスポンスを実際に全件確認したところ、
**下書きが1件も含まれていなかった**（135件全件 `status: "published"`）。
`count_drafts()` はこの一覧を数えて下書き数を判定しているため、
**常に0件と報告し続ける可能性が高い。** 下書き数の正確な把握は、
つなげーとの管理画面で直接確認すること。詳細は `docs/tunagate-api.md` を参照。

### `capacity`（イベント全体の定員）など、まだ送信していないフィールドがある

`GET /api/external/events/:id`（`show` コマンド）で実イベントを取得すると、
`place` / `place_detail` / `pref_id` / `capacity`（イベント全体）/ `min_num_of_people` /
`application_due_date` / `event_end_datetime` など、このリポジトリの `create` が
**まだ送信していないフィールド**が複数見つかった。詳細と対応状況は `docs/tunagate-api.md`
の「未対応・要検証のフィールド」を参照。
