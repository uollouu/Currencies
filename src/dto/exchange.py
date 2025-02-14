from dataclasses import dataclass
from src.dto.currencies import CurrencyDTO
from src.dto.basedto import DTO
@dataclass
class ExchangeDTO(DTO):
    base_currency: CurrencyDTO
    target_currency: CurrencyDTO
    rate: float
    amount: float
    converted_amount: float

    def tojson(self):
        data_table = {
            "baseCurrency" : self.base_currency.tojson(),
            "targetCurrency" : self.target_currency.tojson(),
            "rate" : self.rate,
            "amount" : self.amount,
            "convertedAmount" : self.converted_amount
        }
        return data_table

