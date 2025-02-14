from typing import Any, Optional
from abc import ABC, abstractmethod

import pandas as pd
from adaptix import Retort

from src.dto.exchange_rates import ExchangeRateDTO, ExchangeRatesDTO
from src.dto.exchange import ExchangeDTO
from src.utils.exceptions import (ExchangeRateNotFoundError,
                                  CurrencyNotFoundError,
                                  ExchangeUnavailableError, ExchangeRateAlreadyExistsError, ForeignKeyError)

from src.dto.currencies import DTO, CurrencyDTO, CurrenciesDTO
from src.model.dao import DAO, CurrenciesDAO, ExchangeRatesDAO
from src.utils.singleton import Singleton
from src.utils.split_string_combos import split_string_combos

retort = Retort()
class Service(ABC, Singleton):
    pass

class DAOService(Service):

    @property
    @abstractmethod
    def _DAO(self) -> DAO:
        pass

    @abstractmethod
    def get_one(self, *args, **kwargs) -> DTO:
        pass

    @abstractmethod
    def get_all(self) -> DTO:
        pass

    @abstractmethod
    def add(self, *args, **kwargs) -> DTO:
        pass

class CurrenciesService(DAOService):
    _DAO = CurrenciesDAO()

    @staticmethod
    def get_currency_dto(currency_dict: dict[str, Any]) -> CurrencyDTO:
        return retort.load(currency_dict, CurrencyDTO)

    def get_one(self, currency_id: Optional[int] = None,
                        currency_code: Optional[str] = None) -> CurrencyDTO:
        currency_data: pd.DataFrame = self._DAO.get_one(id=currency_id, code=currency_code)

        if currency_data.empty:
            raise CurrencyNotFoundError

        currency_dict: dict[str, any] = currency_data.to_dict(orient='records')[0]

        currency: CurrencyDTO = retort.load(currency_dict, CurrencyDTO)

        return currency

    def get_all(self) -> CurrenciesDTO:
        currencies_data: pd.DataFrame = self._DAO.get_all()
        currencies_list: list[dict[str, Any]] = currencies_data.to_dict(orient='records')

        currencies: CurrenciesDTO = retort.load({"currencies": currencies_list}, CurrenciesDTO)

        return currencies

    def add(self, name: str, code: str, sign: str) -> CurrencyDTO:
        self._DAO.insert(name, code, sign)

        return self.get_one(currency_code=code)

class ExchangeRatesService(DAOService):
    _DAO = ExchangeRatesDAO()
    _currencies_service = CurrenciesService()

    def get_one(self, base_currency_code, target_currency_code) -> ExchangeRateDTO:
        try:
            base_currency = self._currencies_service.get_one(currency_code=base_currency_code)
            target_currency = self._currencies_service.get_one(currency_code=target_currency_code)

            exchange_rate_data = self._DAO.get_one(base_currency.id, target_currency.id)

            if not exchange_rate_data.empty:
                exchange_rate_dict = exchange_rate_data.to_dict(orient="records")[0]
                er_id = exchange_rate_dict["id"]
                er_rate = exchange_rate_dict["rate"]

                exchange_rate_dto = ExchangeRateDTO(er_id,
                                                    base_currency,
                                                    target_currency,
                                                    er_rate)
                return exchange_rate_dto

        except CurrencyNotFoundError:
            pass

        raise ExchangeRateNotFoundError

    def get_all(self) -> ExchangeRatesDTO:
        exchange_rates_data: pd.DataFrame = self._DAO.get_all()
        exchange_rates_list: list[dict[str, Any]] = exchange_rates_data.to_dict(orient="records")

        exchange_rates_dto = ExchangeRatesDTO()

        for er_dict in exchange_rates_list:
            base_id = er_dict["base_currency_id"]
            target_id = er_dict["target_currency_id"]

            base_currency_dto = self._currencies_service.get_one(currency_id=base_id)
            target_currency_dto = self._currencies_service.get_one(currency_id=target_id)

            exchange_rate_dto = ExchangeRateDTO(id=er_dict["id"],
                                                baseCurrency=base_currency_dto,
                                                targetCurrency=target_currency_dto,
                                                rate=er_dict["rate"])
            exchange_rates_dto.append(exchange_rate_dto)

        return exchange_rates_dto

    def add(self, base_currency_code, target_currency_code, rate):
        base_currency: CurrencyDTO = self._currencies_service.get_one(currency_code=base_currency_code)
        target_currency: CurrencyDTO = self._currencies_service.get_one(currency_code=target_currency_code)

        if self.exchange_rate_exists(base_currency.id, target_currency.id):
            raise ExchangeRateAlreadyExistsError

        self._DAO.insert(base_currency.id, target_currency.id, rate)

        return self.get_one(base_currency_code, target_currency_code)

    def exchange_rate_exists(self, base_currency_id, target_currency_id):
        return not self._DAO.get_one(base_currency_id, target_currency_id).empty

class ExchangeService(Service):
    _cross_currency = "USD"
    _exchange_rates_service = ExchangeRatesService()
    def __init__(self):
        self._exchange_ways = (self._get_fb, self._get_cross)

    def get(self, base_currency_code: str,
            target_currency_code: str,
            amount: float) -> ExchangeDTO:

        for exchange_way in self._exchange_ways:
            try:
                exchange_dto: ExchangeDTO = exchange_way(base_currency_code,
                                            target_currency_code, amount)
                return exchange_dto

            except ExchangeUnavailableError:
                pass

        raise ExchangeUnavailableError



    def _get_cross(self, base_currency_code: str,
                   target_currency_code: str,
                   amount: float) -> ExchangeDTO:
        try:
            base_usd_exchange: ExchangeDTO = self._get_fb(base_currency_code, self._cross_currency, amount)
            usd_target_exchange: ExchangeDTO = self._get_fb(self._cross_currency, target_currency_code, amount)

        except ExchangeRateNotFoundError:
            raise ExchangeUnavailableError

        base_currency: CurrencyDTO = base_usd_exchange.base_currency
        target_currency: CurrencyDTO = usd_target_exchange.target_currency
        rate: float = base_usd_exchange.rate * usd_target_exchange.rate
        converted_amount = amount * rate

        exchange_dto: ExchangeDTO = ExchangeDTO(base_currency,
                                                target_currency,
                                                rate,
                                                amount,
                                                converted_amount)

        return exchange_dto

    def _get_fb(self, base_currency_code: str,
                target_currency_code:str,
                amount:float):
        try:
            exchange_dto = self._get_forward(base_currency_code,
                                             target_currency_code,
                                             amount)
            return exchange_dto

        except ExchangeUnavailableError:
            exchange_dto = self._get_backward(base_currency_code,
                                              target_currency_code,
                                              amount)
            return exchange_dto

    def _get_forward(self, base_currency_code: str,
                    target_currency_code: str,
                    amount: float) -> ExchangeDTO:

        try:
            exchange_rate: ExchangeRateDTO = self._exchange_rates_service.get_one(base_currency_code,
                                                                                  target_currency_code)
        except ExchangeRateNotFoundError:
            raise ExchangeUnavailableError

        converted_amount: float = amount * exchange_rate.rate

        exchange_dto: ExchangeDTO = ExchangeDTO(exchange_rate.baseCurrency,
                                               exchange_rate.targetCurrency,
                                               exchange_rate.rate,
                                               amount,
                                               converted_amount)
        return exchange_dto

    def _get_backward(self, base_currency_code: str,
                     target_currency_code: str,
                     amount: float) -> ExchangeDTO:

        try:
            exchange_rate = self._exchange_rates_service.get_one(target_currency_code,
                                                                              base_currency_code)
        except ExchangeRateNotFoundError:
            raise ExchangeUnavailableError

        base_currency: CurrencyDTO = exchange_rate.targetCurrency
        target_currency: CurrencyDTO = exchange_rate.baseCurrency
        rate = 1/exchange_rate.rate
        converted_amount: float = amount * rate

        exchange_dto: ExchangeDTO = ExchangeDTO(base_currency,
                                                target_currency,
                                                rate,
                                                amount,
                                                converted_amount)
        return exchange_dto


    # def get_indirectly(self, base_currency_code: str,
    #                  target_currency_code: str,
    #                  amount: float,
    #         exchange_rate1: ExchangeDTO = self._get_fb(base_currency_code, target_currency_code, amount)
    #     except







#
#         self._DAO.create(name, code, sign)
#
#
# class GetCurrenciesService(Service):
#     _DAO = CurrenciesDAO()
#
#     def get_dto(self) -> CurrenciesDTO:
#         currencies_data: DataTable = self._DAO.get()
#         currencies_list: list[dict[str, Any]] = currencies_data.tolist()
#
#         currencies: CurrenciesDTO = retort.load({"currencies": currencies_list}, CurrenciesDTO)
#
#         return currencies
#
#
# class GetCurrencyService(Service):
#     _DAO = CurrencyDAO()
#
#     def __init__(self, currency_code: str) -> None:
#         self.currency_code = currency_code
#
#     def get_dto(self) -> CurrencyDTO:
#         currency_data: DataTable = self._DAO.get(self.currency_code)
#
#         if currency_data.empty():
#             raise CurrencyNotFoundError
#
#         currency_dict: dict[str, any] = currency_data.todict(0)
#
#         currencies: CurrencyDTO = retort.load(currency_dict, CurrencyDTO)
#
#         return currencies
#
# class PostCurrencyService(CurrencyService):
#     def __init__(self, currency_dto):
#
# class Service:
#     def __init__(self):
#         self.__DAO = DAO()
#
#     def get_currency(self, currency_code: str):
#         currency_data: DataTable = self.__DAO.get_currency(currency_code)
#         currency_dict: dict[str, any] = currency_data.todict(0)
#
#         currencies: CurrencyDTO = retort.load(currency_dict, CurrencyDTO)
#
#         return currencies
#
#     def get_currencies(self):
#         currencies_data: DataTable = self.__DAO.get_currencies()
#         currencies_list: list[dict[str, Any]] = currencies_data.tolist()
#
#         currencies: CurrenciesDTO = retort.load({"currencies" : currencies_list}, CurrenciesDTO)
#
#         return currencies
#






