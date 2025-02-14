import json
from typing import Any
from dataclasses import dataclass
from src.dto.basedto import DTO


@dataclass
class CurrencyDTO(DTO):
    id: int
    name: str
    code: str
    sign: str

    def tojson(self) -> str:
        data_table: dict[str, Any] = {
        "id": self.id,
        "name": self.name,
        "code": self.code,
        "sign": self.sign
        }
        return data_table

@dataclass
class CurrenciesDTO(DTO):
    currencies: list[CurrencyDTO]

    def tojson(self) -> str:
        currencies_jsons: list[str] = []

        for currency_dto in self.currencies:
            currencies_jsons.append(currency_dto.tojson())

        return currencies_jsons

