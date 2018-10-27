import csv

with open("top_cities.csv", "w", newline="") as f:

    writer = csv.writer(f)
    writer.writerow(["ank", "city", "population"])

    writer.writerows([
        [1, "上海", 24150000],
        [2, "カラチ", 2350000],
        [3, "北京", 2151000]
    ])
