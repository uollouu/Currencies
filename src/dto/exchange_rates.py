from dataclasses import dataclass
import json

from src.dto.currencies import CurrencyDTO
from src.dto.basedto import DTO

@dataclass
class ExchangeRateDTO(DTO):
    id: int
    baseCurrency: CurrencyDTO
    targetCurrency: CurrencyDTO
    rate: float

    def tojson(self) -> dict:
        data_table = {
            "id" : self.id,
            "baseCurrency" : self.baseCurrency.tojson(),
            "targetCurrency" : self.targetCurrency.tojson(),
            "rate" : self.rate
        }
        return data_table

class ExchangeRatesDTO(DTO):
    def __init__(self) -> None:
        self.__exchange_rates: list[ExchangeRateDTO] = []

    def append(self, exchange_rate: ExchangeRateDTO) -> None:
        self.__exchange_rates.append(exchange_rate)

    def tojson(self) -> list:
        exchange_rates_jsons = []

        for exchange_rate in self.__exchange_rates:
            exchange_rates_jsons.append(exchange_rate.tojson())

        return exchange_rates_jsons
