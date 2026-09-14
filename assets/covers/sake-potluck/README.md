# 日本酒持ち寄り会 — イベント表紙

| ファイル | 中身 |
|---|---|
| `cover.png` | 書き出し済みの表紙。1200 × 1600 px（縦横比 3:4） |
| `cover@2x.png` | 同じ絵の高解像度版。2400 × 3200 px。印刷や拡大用 |
| `cover.svg` | 元データ。フォントを埋め込んであるので単体で開けます |
| `gen.py` | `cover.svg` / `cover.html` を生成するスクリプト |
| `fetchfont.py` | Google Fonts から使用文字だけを取り出して `fonts.json` に保存 |

## 載せている文言

- メイン: 日本酒持ち寄り会
- サブ: 好きな一本を持ち寄って、ゆるく乾杯
- タグ: 持ち寄り歓迎 / 飲みくらべ / はじめまして歓迎
- 下帯: ひとりでの参加も大丈夫です / 20歳以上／飲酒の強要はしません

下帯の2行は `brand/rules.md` の 1番（20歳以上）と 5番（飲酒の強要はしない）に合わせています。

日時・会場・参加費は**あえて画像に入れていません**。確定していないためです。
募集ページ本文（`events/<日付>-<slug>/recruit.md`）側に書くか、確定後にこの表紙へ追記してください。

## 作り直しかた

```bash
python3 fetchfont.py   # fonts.json を作る（ネットワークが必要）
python3 gen.py         # cover.svg と cover.html を書き出す

# PNG へ（Chromium のビューポートが指定より低く出るので、大きめに撮って切り出す）
"$CHROMIUM" --headless --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1200,1780 \
  --screenshot=raw.png file://$PWD/cover.html
python3 - <<'PY'
from PIL import Image
im = Image.open("raw.png").convert("RGB").crop((0, 0, 2400, 3200))
im.save("cover@2x.png")
im.resize((1200, 1600), Image.LANCZOS).save("cover.png", optimize=True)
PY
```

## 直したいときの目印（`gen.py`）

- 文言: `build()` の後半、`--- 文字まわり` 以降
- 人物の配置: `--- 後列` / `--- 前列` の `person(...)` 呼び出し（x, y, 拡大率, 髪型, 服の色…）
- 色: 先頭の `C` / `SKIN` / `HAIR` / `CLOTH`
- テーブルの小物: `--- テーブル` の `bottle` / `tokkuri` / `ochoko` / `masu` / `edamame`
