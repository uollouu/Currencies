import sqlite3
from pathlib import Path
import sys

con = sqlite3.connect("db/currency_exchange.db")
cur = con.cursor()
cur.execute("""
select * from currencies""")
print(cur.fetchall(), cur.description)
