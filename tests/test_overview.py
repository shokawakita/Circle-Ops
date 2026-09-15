import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts" / "tunagate"))

import overview  # noqa: E402


GOOD = """\
# 2610-ID_ボードゲーム会

## イベント概要

【募集タイトル】横浜ではじめましてのボードゲーム会
【メイン画像】https://example.com/images/2610.png
【定員】12

【参加費】
| チケット名 | 価格 | 定員 | 販売期限 |
|---|---|---|---|
| 早割 | 2500 | 5 | 2026-10-05 23:59 |
| 通常 | 3000 | 7 |  |

## 募集本文

はじめましての方も、ひとりでも大丈夫です。

キャンセルは前日までにご連絡ください。
"""


class ParseGood(unittest.TestCase):
    def setUp(self):
        self.r = overview.parse(GOOD)

    def test_no_errors(self):
        self.assertEqual(self.r.errors, [])
        self.assertTrue(self.r.ok)

    def test_title_is_the_public_one(self):
        self.assertEqual(self.r.title, "横浜ではじめましてのボードゲーム会")

    def test_capacity(self):
        self.assertEqual(self.r.capacity, 12)

    def test_plans(self):
        self.assertEqual(len(self.r.plans), 2)
        early, normal = self.r.plans
        self.assertEqual(early.name, "早割")
        self.assertEqual(early.price, 2500)
        self.assertEqual(early.capacity, 5)
        self.assertEqual(early.expired_at, "2026-10-05T23:59:00")
        self.assertEqual(normal.price, 3000)
        self.assertIsNone(normal.expired_at, "空欄の販売期限は無期限扱い")

    def test_body_excludes_the_overview(self):
        self.assertIn("ひとりでも大丈夫", self.r.body)
        self.assertNotIn("【募集タイトル】", self.r.body)

    def test_body_keeps_its_own_subheadings(self):
        # 募集文は「当日の流れ」「お願い」「キャンセルについて」を見出しで持つ。
        # ここで切られると規約とキャンセルポリシーが本文から落ちる。
        md = GOOD + "\n## 当日の流れ\n\n受付のあと自己紹介です。\n\n## キャンセルについて\n\n前日までにご連絡ください。\n"
        r = overview.parse(md)
        self.assertIn("当日の流れ", r.body)
        self.assertIn("キャンセルについて", r.body)


class Normalization(unittest.TestCase):
    def test_full_width_and_units(self):
        md = GOOD.replace("【定員】12", "【定員】１２名").replace("| 早割 | 2500 |", "| 早割 | 2,500円 |")
        r = overview.parse(md)
        self.assertEqual(r.errors, [])
        self.assertEqual(r.capacity, 12)
        self.assertEqual(r.plans[0].price, 2500)

    def test_bullet_prefix_is_tolerated(self):
        md = GOOD.replace("【定員】12", "- 【定員】12")
        self.assertEqual(overview.parse(md).capacity, 12)


class MissingPieces(unittest.TestCase):
    def test_missing_title_is_an_error(self):
        md = GOOD.replace("【募集タイトル】横浜ではじめましてのボードゲーム会\n", "")
        r = overview.parse(md)
        self.assertIsNone(r.title)
        self.assertTrue(any(overview.KEY_TITLE in e for e in r.errors))

    def test_missing_price_table_is_an_error(self):
        md = GOOD.split("【参加費】")[0] + "\n## 募集本文\n\n本文\n"
        r = overview.parse(md)
        self.assertEqual(r.plans, [])
        self.assertTrue(any("チケット" in e or "参加費" in e for e in r.errors))

    def test_missing_overview_heading(self):
        r = overview.parse("## 募集本文\n\n本文\n")
        self.assertFalse(r.ok)

    def test_image_is_optional(self):
        md = GOOD.replace("【メイン画像】https://example.com/images/2610.png\n", "")
        r = overview.parse(md)
        self.assertEqual(r.errors, [])
        self.assertIsNone(r.image_url)


class BadValues(unittest.TestCase):
    def test_notion_signed_url_is_rejected(self):
        md = GOOD.replace(
            "https://example.com/images/2610.png",
            "https://prod-files-secure.s3.us-west-2.amazonaws.com/x.png?X-Amz-Signature=abc",
        )
        r = overview.parse(md)
        self.assertTrue(any("署名付きURL" in e for e in r.errors))

    def test_non_https_image_is_rejected(self):
        md = GOOD.replace("https://example.com/images/2610.png", "example.com/x.png")
        self.assertTrue(any("https" in e for e in overview.parse(md).errors))

    def test_bad_expiry_format(self):
        md = GOOD.replace("2026-10-05 23:59", "10/5")
        self.assertTrue(any("販売期限" in e for e in overview.parse(md).errors))

    def test_unreadable_price(self):
        md = GOOD.replace("| 通常 | 3000 |", "| 通常 | 応相談 |")
        self.assertTrue(any("価格" in e for e in overview.parse(md).errors))


class TodoIsNeverSent(unittest.TestCase):
    """CLAUDE.md: 不明な値は TODO: のまま残し、埋めた体で進めない。"""

    def test_todo_title_is_rejected(self):
        md = GOOD.replace("【募集タイトル】横浜ではじめましてのボードゲーム会", "【募集タイトル】TODO:")
        r = overview.parse(md)
        self.assertIsNone(r.title, "TODO: のタイトルを送ってはいけない")
        self.assertFalse(r.ok)

    def test_todo_capacity_is_rejected(self):
        md = GOOD.replace("【定員】12", "【定員】TODO:")
        r = overview.parse(md)
        self.assertIsNone(r.capacity)
        self.assertFalse(r.ok)

    def test_todo_image_is_rejected(self):
        md = GOOD.replace("【メイン画像】https://example.com/images/2610.png", "【メイン画像】TODO:")
        r = overview.parse(md)
        self.assertIsNone(r.image_url)
        self.assertFalse(r.ok)

    def test_the_repo_template_never_passes(self):
        tpl = pathlib.Path(__file__).resolve().parents[1] / "events" / "_template" / "notion-page.md"
        r = overview.parse(tpl.read_text("utf-8"))
        self.assertFalse(r.ok, "雛形が素通りしたら TODO: のまま公開されうる")
        self.assertIsNone(r.title)


if __name__ == "__main__":
    unittest.main()
