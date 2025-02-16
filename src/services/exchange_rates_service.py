from typing import Any

import pandas as pd

from src.dto.currencies import CurrencyDTO
from src.dto.exchange_rates import ExchangeRateDTO, ExchangeRatesDTO
from src.model.dao import ExchangeRatesDAO
from src.services.currencies_service import CurrenciesService
from src.services.base_service import DAOService
from src.utils.exceptions import (CurrencyNotFoundError,
                                  ExchangeRateNotFoundError,
                                  ExchangeRateAlreadyExistsError)



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

    def add(self, base_currency_code: str, target_currency_code: str, rate: float):
        base_currency: CurrencyDTO = self._currencies_service.get_one(currency_code=base_currency_code)
        target_currency: CurrencyDTO = self._currencies_service.get_one(currency_code=target_currency_code)

        if self.exchange_rate_exists(base_currency.id, target_currency.id):
            raise ExchangeRateAlreadyExistsError

        self._DAO.insert(base_currency.id, target_currency.id, rate)

        return self.get_one(base_currency_code, target_currency_code)

    def exchange_rate_exists(self, base_currency_id, target_currency_id):
        return not self._DAO.get_one(base_currency_id, target_currency_id).empty
