from src.dto.currencies import CurrencyDTO
from src.dto.exchange import ExchangeDTO
from src.dto.exchange_rates import ExchangeRateDTO
from src.services.base_service import Service
from src.services.exchange_rates_service import ExchangeRatesService
from src.utils.exceptions import ExchangeUnavailableError, ExchangeRateNotFoundError


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
