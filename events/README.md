# events

1イベント1ディレクトリ。`_template/` を複製して使います。

```
events/YYYY-MM-DD-slug/
├ plan.md      企画・目的・ターゲット・成功の定義
├ recruit.md   募集文（そのまま告知に貼れる状態）
├ script.md    当日の進行台本
├ pl.md        収支（事前シミュレーション → 開催後に確定値で上書き）
└ retro.md     振り返り（開催後に記入）
```

`notion-page.md` は Notion の `TEST_Event_Projects_DB` に作るページ本文の雛形です
（`events/YYYY-MM-DD-slug/` には置かず、複製して Notion に貼ります）。

`/event-repeat` を使えば、過去のイベントから Notion ページとつなげーとの下書きが作られます。
`/event-new` を使えばこの一式が自動で作られます。
`/event-close` を使えば `pl.md` の確定と `retro.md` の記入まで進みます。

命名例: `events/2026-09-13-boardgame-yokohama/`
