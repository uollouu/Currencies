
import json

from adaptix import Retort

from src.db.table_config import TableConfig
from src.utils.paths import TABLES_CONFIG

retort = Retort()

def load_tables_config():
    tables_config: list[TableConfig]

    with open(TABLES_CONFIG, "r") as file:
        tables_config = retort.load(json.load(file), list[TableConfig])

    return tables_config
