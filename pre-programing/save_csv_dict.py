import csv

#with open("top_cities2.csv", "w", newline="") as f:
#shift_jis
with open("top_cities2.csv", "w", newline="", encoding="cp932") as f:

    writer = csv.DictWriter(f, ["rank", "city", "population"])
    writer.writeheader()

    writer.writerows([
        {"rank": 1, "city": "上海", "population": 24150000},
        {"rank": 2, "city": "カラチ", "population": 23500000},
        {"rank": 3, "city": "北京", "population": 21516000},
        {"rank": 4, "city": "天津", "population": 14722100},
    ])