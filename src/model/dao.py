import sqlite3
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional

from src.model.dbmanager import DBManager
from src.utils.singleton import Singleton
from src.utils.exceptions import ForeignKeyError

SELECT_CURRENCIES = """
    select ID id , FullName name, Code code, Sign sign 
    from currencies
    """
SELECT_EXCHANGE_RATES = """
    select ID id, 
    BaseCurrencyID base_currency_id, 
    TargetCurrencyID target_currency_id, 
    Rate rate
    from ExchangeRates
    """

INSERT_CURRENCY = """
    insert into Currencies (fullname, code, sign)
    values (?, ?, ?)
    """

INSERT_EXCHANGE_RATE = """
    insert into exchangeRates (baseCurrencyId, targetCurrencyId, rate)
    values (?, ?, ?)
    """

class DAO(ABC, Singleton):

    def __init__(self) -> None:
        self._db_manager = DBManager()

    def _execute_query(self, query, params: Optional[list[str]] = None) -> pd.DataFrame:
        return self._db_manager.execute_query(query, params)

    def _execute_dml(self, statement, params: Optional[list[str]] = None):
        try:
            self._db_manager.execute_dml(statement, params)
        except sqlite3.IntegrityError:
            raise ForeignKeyError

    @abstractmethod
    def get_all(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def insert(self, *args, **kwargs) -> None:
        pass


class CurrenciesDAO(DAO):
    def get_all(self) -> pd.DataFrame:
        currencies_data: pd.DataFrame = self._execute_query(SELECT_CURRENCIES)

        return currencies_data

    def get_one(self, id: Optional[int] = None, code: Optional[str] = None):
        params = [p for p in (id, code) if p]
        currency_data: pd.DataFrame = self._execute_query(f"""
            {SELECT_CURRENCIES}
            where {"id = ? " if id else "1=1"} and
                  {"code = ? " if code else "1=1"}
            """, params)

        return currency_data

    def insert(self, name: str, code: str, sign: str) -> None:
        self._execute_dml(INSERT_CURRENCY, [name, code, sign])


class ExchangeRatesDAO(DAO):
    def get_all(self) -> pd.DataFrame:
        exchange_rates_data: pd.DataFrame = self._execute_query(SELECT_EXCHANGE_RATES)

        return exchange_rates_data

    def get_one(self, base_currency_id, target_currency_id) -> pd.DataFrame:
        exchange_rate_data: pd.DataFrame = self._execute_query(f"""
            {SELECT_EXCHANGE_RATES}
            where BaseCurrencyID = ? and TargetCurrencyID = ?
            """, [base_currency_id, target_currency_id])

        return exchange_rate_data

    def insert(self, base_currency_id, target_currency_id, rate) -> None:
        self._execute_dml(INSERT_EXCHANGE_RATE,
                          [base_currency_id, target_currency_id, rate])


# class CurrencyDAO(DAO):
#     def get(self, currency_code) -> DataTable:
#         currency_data: DataTable = self._execute_query(f"""
#             select ID id , FullName name, Code code, Sign sign
#             from currencies
#             where code = '{currency_code}'
#             """)
#
#         return currency_data
# #
#
# class DAO:
#     def __init__(self) -> None:
#         self.__db_manager = DBManager()
#
#     def get_exchange_rates(self):
#         exchange_rates: DataTable = self.__execute_query("""
#         select ID id, BaseCurrencyID base, TargetCurrencyID, Rate from exchangerates
#         """)
#         print(exchange_rates)
#
#     def get_currencies(self) -> DataTable:
#         currencies_data: DataTable = self.__execute_query("""
#             select ID id, FullName name, Code code, Sign sign
#             from currencies
#             """)
#
#         return currencies_data
#
#     def get_currency(self, currency_code: str) -> DataTable:
#         currency_data: DataTable = self.__execute_query(f"""
#             select ID id , FullName name, Code code, Sign sign
#             from currencies
#             where code = '{currency_code}'
#             """)
#
#         return currency_data
#
#     def __execute_query(self, statement):
#         return self.__db_manager.execute_query(statement)

