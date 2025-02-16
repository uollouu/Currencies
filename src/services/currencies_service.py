from typing import Any, Optional

import pandas as pd
from adaptix import Retort

from src.dto.currencies import CurrencyDTO, CurrenciesDTO
from src.model.dao import CurrenciesDAO
from src.services.base_service import DAOService
from src.utils.exceptions import CurrencyNotFoundError


retort = Retort()


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
