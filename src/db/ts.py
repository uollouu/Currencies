import sqlite3

con = sqlite3.connect("currency_exchange.db")
cur = con.cursor()
t = ()
cur.execute("select * from currencies where code", t)
print(cur.fetchall())