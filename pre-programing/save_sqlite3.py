import sqlite3

conn = sqlite3.connect("top_cities.db")
c = conn.cursor()

c.execute("""
  create table cities (
      rank integer,
      city text,
      population integer
  )
""")

c.execute("insert into cities values (?, ?, ?)", (1, "上海", 2415000))

c.execute("insert into cities values (:rank, :city, :population)", 
   {"rank": 2, "city": "カラチ", "population": 23500000}
)

c.executemany("insert into cities values (:rank, :city, :population)",[
  {"rank": 3, "city": "北京", "population": 21516000},
  {"rank": 4, "city": "天津", "population": 14722100},
  {"rank":  5, "city": "イスタンブル", "population": 14160467}
])

conn.commit()

c.execute("select * from cities")

for row in c.fetchall():
    print(row)

conn.close()