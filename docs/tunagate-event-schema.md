# つなげーと イベント インターフェース定義

`GET /api/external/events/:id`（`scripts/tunagate/cli.py show --id <id>`）で
実際に返ってきたイベント（`event_id 594081` / 2026-09-16 取得）を元に、
フィールドごとの型・桁数・意味を整理したもの。

公式ドキュメント（https://tunagate.com/support/external_api）に型定義の記載が無いため、
**すべて実データ1件からの観測に基づく推定**。桁数・上限は「確認できた例」であり、
それが仕様上の上限とは限らない。仕様が変わった・別の値を見つけたら、この表を直すこと。

**Read（GET）で確認できることと、Write（POST/PATCH）で同じキー名が使えることは別問題。**
読み取り専用フィールド（`id` `public_url` など）はサーバー生成のため書き込み不可。
書き込み可能と思われるフィールドの送信キー名の対応は `scripts/tunagate/field_map.json` を参照
（`_unverified_fields` は未検証、それ以外は create を実行して動作確認済み）。

---

## イベント本体

| フィールド | 型 | 観測値の例 | 桁数・書式 | 意味 | Read | Write |
|---|---|---|---|---|---|---|
| `id` | integer | `594081` | 6桁程度 | つなげーとのイベントID | ✅ | — サーバー生成 |
| `circle_id` | integer | `97956` | 5桁程度 | サークルID | ✅ | ✅ 検証済み（`circle_id`。create時のみ） |
| `title` | string | `【初心者歓迎】渋谷の...🥝` | 実例62文字。絵文字可。上限不明 | 公開タイトル | ✅ | ✅ 検証済み（`event[title]`） |
| `status` | string (enum) | `"published"` | 観測値は `published` のみ。一覧APIが下書きを返さないため `draft` 等の値は未観測 | 公開状態 | ✅ | — サーバー管理 |
| `event_date` | string (datetime) | `"2026-09-23T13:00:00.000+09:00"` | ISO8601、ミリ秒・タイムゾーンオフセット付き | 開催開始日時 | ✅ | ✅ 検証済み（`event[event_date]`） |
| `public_url` | string (URL) | `https://tunagate.com/circle/97956/events/594081` | — | 公開ページURL | ✅ | — サーバー生成 |
| `edit_url` | string (URL) | `https://tunagate.com/event/edit/594081` | — | 編集ページURL | ✅ | — サーバー生成 |
| `body` | string | （実例約2000文字） | 改行・絵文字含む。Markdown装飾は無く `▪️` 等の記号で区切る。上限文字数不明 | 募集本文 | ✅ | ✅ 検証済み（`body`） |
| `place` | string | `"渋谷駅徒歩15分"` | 短文 | 簡易場所表示 | ✅ | ✅ 検証済み（`event[place]`。2026-09-26、event 620449で確認） |
| `place_detail` | string | `"氷川区民会館 集会室"` | 短文 | 会場詳細名 | ✅ | ✅ 検証済み（`event[place_detail]`。2026-09-26、event 620449で確認） |
| `is_online` | boolean | `false` | — | オンライン開催か | ✅ | ⚠️ 未対応（未実装） |
| `online_url` | string \| null | `null` | — | オンラインURL | ✅ | ⚠️ 未対応（未実装） |
| `main_image_url` | string (URL) | `https://image.tunagate.net/uploads/...` | つなげーと自ドメインのCDN | メイン画像 | ✅ | ✅ 検証済み（`main_image_url`） |
| `pref_id` | integer | `13` | 1〜2桁 | 都道府県ID。JIS X 0401の都道府県コードと推測（13=東京都は一致）。他県は未検証 | ✅ | ✅ 検証済み（`event[pref_id]`。2026-09-26、event 620449（`pref_id: 13`）で確認）。対応表は `client.py` の `PREFECTURE_IDS`（東京都・神奈川県のみ登録、他県は未検証のまま） |
| `capacity` | integer | `20` | — | イベント全体の定員。**プラン定員の合計と一致しなくてよい**（早割系が埋まって閉じる設計のため） | ✅ | ✅ 検証済み（`event[capacity]`。2026-09-26、event 620449で確認） |
| `min_num_of_people` | integer | `4` | — | 最小催行人数 | ✅ | ✅ 検証済み（`event[min_num_of_people]`。2026-09-26、event 620449で確認） |
| `application_due_date` | string (datetime) | `"2026-09-23T12:55:00.000+09:00"` | ISO8601。実例は開始5分前 | 申込締切日時 | ✅ | ✅ 検証済み（`event[application_due_date]`。2026-09-26、event 620449で確認） |
| `event_end_datetime` | string (datetime) | `"2026-09-23T17:00:00.000+09:00"` | ISO8601 | 終了日時 | ✅ | ✅ 検証済み（`event[event_end_datetime]`。2026-09-26、event 620449で確認） |
| `is_publicity` | boolean | `true` | — | 公開設定。意味の詳細（`status`との違い）は未確認 | ✅ | ⚠️ 未対応（未実装） |
| `is_new` | boolean | `false` | — | 意味未確認（「新規サークル向け」等の表示フラグと推測） | ✅ | — 用途不明のため未実装 |
| `num_of_participants` | integer | `10` | — | 現在の参加者数。実績値のため作成時には送らない | ✅ | — 読み取り専用（参加処理で増減） |
| `create_user_id` | integer | `520334` | — | 作成者のつなげーとユーザーID | ✅ | — サーバー生成 |

## `plans[]`（チケット）

`events_plans[]` として送るプラン配列。**2026-09-25の実検証で判明: GETと書き込み側のキー名は同じ**
（`plan` / `creator_price`）。当初は書き込み側を `name` / `price`（推定）としていたが誤りで、
実際に送っても無視され `plan: ""` `creator_price: 0` の空チケットが作成されるだけだった。

| フィールド（GET） | 型 | 観測値の例 | 意味 | Read | Write（対応する送信キー） |
|---|---|---|---|---|---|
| `id` | integer | `1135434` | プランID | ✅ | — サーバー生成 |
| `plan` | string | `"【⚠️⚠️進行役専用⚠️⚠️】参加チケット"` | プラン名。`【】`や絵文字を含めてよい | ✅ | ✅ 検証済み（`events_plans[][plan]`。2026-09-25、event 620449で確認。当初 `events_plans[][name]` としていたのは誤り） |
| `capacity` | integer | `5` | そのプランの定員 | ✅ | ✅ 検証済み（`events_plans[][capacity]`） |
| `creator_price` | integer | `500` | 価格（円） | ✅ | ✅ 検証済み（`events_plans[][creator_price]`。2026-09-25、event 620449で確認。当初 `events_plans[][price]` としていたのは誤り） |
| `price_type` | integer (enum) | `3` | 価格タイプ。意味未確認（実例は全プラン`3`で固定） | ✅ | ⚠️ 未対応（未実装。値の意味が分からないため実装を保留） |
| `is_publicity` | boolean | `false` | プラン単位の公開設定。event全体が公開でもプランを非表示にできる可能性（実例は全プラン`false`） | ✅ | ⚠️ 未対応（未実装） |
| `is_application_allowed` | boolean | `true` / `false` | 現在申込可能か。早割が埋まると`false`になる、運用中に変動する値と推測。**作成時に送るべき値か自体が未確認**（送ると「最初から締切済みのチケット」を作ってしまう可能性がある） | ✅ | ⚠️ 未対応（意図的に未実装。要検証） |
| `expired_at` | string (datetime) \| null | `null` | 販売期限。無期限なら`null` | ✅ | ✅ 検証済み（`events_plans[][expired_at]`） |

### ⚠️ `PATCH` で `events_plans[]` を送るとプランが作り直される（要注意）

2026-09-25の検証で判明: `PATCH /api/external/events/:id` に `events_plans[]` を送ると、
既存プランを更新するのではなく、**全プランを削除して新しいプランを作り直す**（`id` が変わる。
実例: `1233041` → `1233045`）。`docs/tunagate-api.md` の「プランの差し替えは公開前のみ・全差し替え方式」
はこの挙動を指している。

**現状の `/event-repeat` は `create`（新規作成）しか使わないため実害はない。** ただし今後
「定員だけ直したい」「価格だけ直したい」のような**更新系コマンド**を作る場合は、
このプランIDの作り直しが次の問題を起こしうる:

- 公開後・参加者がいる状態で `events_plans[]` をPATCHすると、参加者が紐づいていた
  プランIDが消えてしまう可能性がある（参加者の申込データとの整合性が壊れるリスク）
- `is_publicity` / `price_type` / `is_application_allowed` はPATCH時に送っていないため、
  作り直されたプランでは既存の値が失われ、サーバー側のデフォルト値に戻る
  （実例: 検証時に `price_type` が `3` → `0` に変化した）

更新系コマンドを作る際は、事前につなげーと運営に「プランの部分更新方法」を確認するか、
最低限「公開後・参加者がいる場合はプランの更新をブロックする」ガードを入れること。

---

## 検証状況の見方

- **✅ 検証済み**: 実際に `create` を送信し、つなげーとの編集画面で反映を確認したフィールド
- **⚠️ 未検証**: GETレスポンスに存在は確認したが、POST/PATCHで同じキー名（または推測したキー名）が使えるかは未確認。`--dry-run` で送信内容を見てから、必ず一度は実送信して編集画面で反映を確かめること
- **⚠️ 未対応**: 意味や挙動が不明なため、実装自体を保留しているフィールド

## 更新のしかた

新しいフィールドを見つけたら、この表に行を追加し、`docs/tunagate-api.md` の
「未対応・要検証のフィールド」節からもリンクする。検証が取れたら「Write」列を
✅ に変えて、確認した日付をどこかに残す。
