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

`/event-new` を使えばこの一式が自動で作られます。
`/event-close` を使えば `pl.md` の確定と `retro.md` の記入まで進みます。

命名例: `events/2026-09-13-boardgame-yokohama/`

## `_ideas/`

開催日や会場がまだ決まっていない企画の検討メモを置きます。
固まったら `_template/` を複製してイベントのディレクトリを作り、中身を移してください。

- `_ideas/matsuri-yatai.md` — 祭りでの屋台出店。出店ルート・許可の整理・屋台案
