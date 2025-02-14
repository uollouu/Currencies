import os
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent


DB_DIR = SRC / "db"

DB = DB_DIR / "currency_exchange.db"
TABLES_CONFIG = DB_DIR / "tables_config.json"







