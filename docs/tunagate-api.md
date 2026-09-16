# つなげーと 外部API（イベント作成）メモ

出典: https://tunagate.com/support/external_api
自分がクリエイター（管理人）であるサークルのイベントだけを操作できます。

---

## 認証

リクエストヘッダに `Authorization: Bearer <トークン>` を指定します。
トークンは環境変数 `TUNAGATE_API_TOKEN` に保存します。**発行時の表示は一度きり。**

```
export TUNAGATE_API_TOKEN=tg_xxxxxxxxxxxxxxxxxxxxxxxx
```

> 公式の注意書き:
> トークンは環境変数またはパスワードマネージャーに保存し、
> **コード・チャット・公開リポジトリに直接貼り付けない。**
> 漏洩の恐れがある場合はAPIトークン管理ページからすぐに失効し、新しいトークンを発行する。

---

## 作成は2段階（下書き → 公開）

```
① POST /api/external/events        下書き作成。誰にも見えない状態で保存
         ↓
   （任意）編集画面で人が内容を確認
         ↓
② POST /api/external/events/:id/publish   ここで初めて一般公開
```

誤生成をそのまま公開してしまう事故を防ぐための2段階です。
**このサークルでは、②は必ず人の確認を挟みます**（`CLAUDE.md` の方針）。

---

## エンドポイント一覧

| メソッド | パス | 内容 |
|---|---|---|
| POST | `/api/external/events` | 下書き作成（`circle_id` 必須） |
| GET | `/api/external/events?circle_id=` | 一覧（`circle_id` 必須。1ページ50件固定・`page` パラメータで移動） |
| GET | `/api/external/events/:id` | 詳細 |
| PATCH | `/api/external/events/:id` | 更新（プランの差し替えは**公開前のみ・全差し替え方式**） |
| POST | `/api/external/events/:id/publish` | 公開（`event_date` と有効なプラン1件以上が必須） |
| DELETE | `/api/external/events/:id` | 削除（他の参加者がいる場合は 422 で拒否） |

---

## 主要パラメータ

| パラメータ | 必須 | 説明 |
|---|---|---|
| `circle_id` | 必須 | 対象サークルID（**create のみ指定**。クリエイター権限を持つサークルのみ） |
| `event[title]` | 必須 | タイトル |
| `event[event_date]` | 公開時必須 | 開催日時 |
| `body` | 任意 | 本文（説明文） |
| `main_image_url` | 任意 | メイン画像のURL。**取得に失敗した場合はリクエスト自体が422で失敗** |
| `events_plans[][...]` | 任意 | プラン配列。**省略時は無料プラン1件が自動生成**（公開には有効なプラン1件以上が必須） |
| `events_plans[][expired_at]` | 任意 | プランの販売期限（早割チケット等に） |

フォームエンコード（`-d "event[title]=..."`）のネスト形式です。

---

## curl 実行例

```bash
# 下書き作成
curl -X POST https://tunagate.com/api/external/events \
  -H "Authorization: Bearer $TUNAGATE_API_TOKEN" \
  -d "circle_id=123" \
  -d "event[title]=もくもく会" \
  -d "event[event_date]=2099-01-01T19:00:00"

# 公開（レスポンスの id を使う）
curl -X POST https://tunagate.com/api/external/events/456/publish \
  -H "Authorization: Bearer $TUNAGATE_API_TOKEN"
```

---

## エラーコード

エラー時のレスポンスボディは常に `{ "error": "メッセージ" }` の形式です。

| ステータス | 意味 |
|---|---|
| 401 | トークンが無効・失効・期限切れ |
| 404 | 権限が無い、またはリソースが存在しない（**権限の有無は区別されない**） |
| 422 | 入力エラー・**下書き上限（10件）超過**・公開条件未達 など |

---

## 運用上、先に効いてくる制約

| 制約 | 対応 |
|---|---|
| **下書きは10件まで** | 溜めっぱなしにすると新規作成が422で落ちる。作成前に GET で下書き数を数え、不要な下書きは消す |
| **`main_image_url` の取得失敗でリクエスト全体が422** | 画像URLは事前に到達確認する。**Notion添付の署名付きURLは数分で失効するため、そのまま渡さない** |
| **プランの差し替えは公開前のみ・全差し替え方式** | 価格や定員を直すなら公開前に。PATCH では配列を丸ごと送る（差分ではない） |
| **プラン省略＝無料プラン1件が自動生成** | 参加費ありの回でプランを渡し忘れると、無料イベントとして公開されうる。**プラン必須チェックを入れる** |
| 404 が権限不足と不在を区別しない | 失敗時に「消えた」と誤判定しない。`circle_id` とトークンの持ち主を先に確認する |
| 一覧は1ページ50件固定 | `page` で回す |
| 参加者がいると DELETE が422 | 削除は基本使わない。中止は Notion 側のステータスで管理する |
