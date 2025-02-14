import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, TypeVar, Generic

from src.utils.singleton import Singleton
from src.utils.paths import DB
from src.db.table_config import TableConfig
from src.db.config_loader import load_tables_config

T = TypeVar('T')

class SupportsLenAndGetItem(Generic[T]):
    pass

def manage_connection(func):

    def wrapper(self, *args, **kwargs):

        already_connected = self.is_connected()

        if not already_connected:
            self._open_connection()

        result = func(self,*args, **kwargs)

        if not already_connected:
            self._close_connection()

        return result
    return wrapper

class DBManager(Singleton):
    __DB: Path = DB

    def __init__(self) -> None:

        creation_required: bool = False
        if not self.__DB.exists():
            creation_required = True

        self._connection: sqlite3.Connection = sqlite3.Connection(self.__DB)
        self._cursor: sqlite3.Cursor = self._connection.cursor()

        self._close_connection()

        if creation_required:
            self.__create_database(load_tables_config())

    @manage_connection
    def _execute(self, statement, params: Optional[list[str]] = None) -> None:
        self._cursor.execute("PRAGMA foreign_keys = ON")
        if params:
            self._cursor.execute(statement, params)
        else:
            self._cursor.execute(statement)

    @manage_connection
    def execute_query(self, query: str, params: Optional[list[str]] = None) -> pd.DataFrame:
        self._execute(query, params)

        result: sqlite3.Cursor = self._cursor

        rows: tuple[tuple, ...] = tuple(result.fetchall())
        col_names: tuple[str, ...] = tuple(str(i[0]).lower() for i in result.description)

        return pd.DataFrame(data=rows, columns=col_names)

    @manage_connection
    def execute_dml(self, statement: str, params: Optional[list[str]] = None) -> None:
        self._execute(statement, params)
        self._connection.commit()

    @manage_connection
    def execute_ddl(self, statement: str, params: Optional[list[str]] = None) -> None:
        self._execute(statement, params)

    @manage_connection
    def __create_database(self, tables_config):

        for table_config in tables_config:
            self.__create_table(table_config)
            self.__fill_table(table_config)

        self._connection.commit()

    @manage_connection
    def __create_table(self, table_config: TableConfig):
        self.execute_ddl(f"""
            create table {table_config.name}
            ({table_config.columns_data})
            """)

    @manage_connection
    def __fill_table(self, table_config: TableConfig):
        rows = table_config.fill_data.rows
        columns = table_config.fill_data.columns
        for row in rows:
            self.execute_dml(f"""
                insert into {table_config.name} 
                {tuple(columns)}
                values {tuple(row)}
                """)

    def _open_connection(self) -> None:
        self._connection = sqlite3.connect(self.__DB)
        self._cursor = self._connection.cursor()

    def _close_connection(self) -> None:
        self._cursor.close()
        self._connection.close()

    def is_connected(self):
        try:
            self._connection.cursor()
            return True
        except sqlite3.ProgrammingError:
            return False

