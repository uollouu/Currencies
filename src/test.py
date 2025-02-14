import os
import pprint
import sqlite3
from abc import ABC, abstractmethod

from src.utils.paths import DB

con = sqlite3.connect(DB)
cur = con.cursor()
try:
    cur.execute("""
    insert into exchangeRates (basecurrencyid, targetCurrencyid, rate)
    values
    (10, 20, 30)""")
    print(cur.execute("select * from exchangeRates").fetchall())
except Exception as err:
    print(err)