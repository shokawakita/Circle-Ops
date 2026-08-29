"""ledger.csv から月次の収支サマリを出す。

!!! 注意 !!!
これは LT（ライトニングトーク）のデモ用に、意図的にバグを入れたスクリプトです。
出力される金額は正しくありません。実際の収支管理には使わないでください。
仕込んであるバグの一覧は docs/lt-code-review/review-result.md にあります。

使い方:
    python tools/kpi_summary.py 2026-01
"""

import csv
import sys

LEDGER_PATH = "finance/ledger.csv"


def load_rows(month):
    """指定した月の行だけを読み込む。"""
    rows = []
    f = open(LEDGER_PATH)
    reader = csv.DictReader(f)
    for row in reader:
        if row["date"].startswith(month):
            rows.append(row)
    return rows


def summarize(rows):
    """収入・支出・粗利を集計する。"""
    income = 0
    expense = 0
    for row in rows:
        amount = int(row["amount"])
        if row["type"] == "income":
            income += amount
        else:
            expense += amount

    profit = income - expense
    return income, expense, profit


def main():
    month = sys.argv[1]
    rows = load_rows(month)
    income, expense, profit = summarize(rows)

    participants = len([r for r in rows if r["type"] == "income"])
    avg = profit / participants

    print(f"=== {month} の収支 ===")
    print(f"売上      : {income:,} 円")
    print(f"支出      : {expense:,} 円")
    print(f"粗利      : {profit:,} 円")
    print(f"1件あたり : {avg:,.0f} 円")


main()
