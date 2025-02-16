from functools import partial
from urllib.parse import urlparse, parse_qs
from typing import Optional, Callable
import json

from src.dto.exchange import ExchangeDTO
from src.utils.exceptions import (RequestException,
                                  CurrencyCodeNotSpecifiedError,
                                  QueryFieldNotSpecifiedError,
                                  InvalidCurrencyCodeError,
                                  InvalidPathError, InvalidAmountError)
from src.services.base_service import Service
from src.services.currencies_service import CurrenciesService
from src.services.exchange_service import ExchangeService
from src.services.exchange_rates_service import ExchangeRatesService
from src.dto.httpresponse import HTTPResponseData
from src.dto.basedto import DTO
from src.utils.parse import parse_query
from src.utils.singleton import Singleton
from src.utils.fpath import FPath


class ServiceClient(Singleton):
    def __init__(self):
        self.currencies_service = CurrenciesService()
        self.exchange_rates_service = ExchangeRatesService()
        self.exchange_service = ExchangeService()

    def get(self, urlpath: str) -> DTO:
        path = urlparse(urlpath)
        fpath = FPath(path.path)
        query = parse_query(path.query)

        if fpath.match("/currencies"):
            return self.currencies_service.get_all()

        if fpath.match("/currency/*"):
            currency_code = fpath[1]
            return self.currencies_service.get_one(currency_code=currency_code)


        if fpath.match("/exchangeRates"):
            return self.exchange_rates_service.get_all()

        if fpath.match("/exchangeRate/*"):
            currencies_codes = fpath[1]

            if len(currencies_codes) != 6:
                raise InvalidCurrencyCodeError

            currency_code1, currency_code2 = currencies_codes[:3], currencies_codes[3:]

            return self.exchange_rates_service.get_one(currency_code1, currency_code2)

        if fpath.match("/exchange"):
            if len(query) > 3:
                raise InvalidPathError
            try:
                base_currency_code: str = query["from"]
                target_currency_code: str = query["to"]
                amount: str = query["amount"]

                try:
                    amount: float = float(amount)
                except ValueError:
                    raise InvalidAmountError

                if len(base_currency_code) != 3 or len(target_currency_code)!= 3:
                    raise InvalidCurrencyCodeError


                exchange: ExchangeDTO = self.exchange_service.get(
                                            base_currency_code,
                                              target_currency_code,
                                          amount)
                return exchange
            except KeyError:
                raise QueryFieldNotSpecifiedError

        if fpath.match("/currency"):
            raise CurrencyCodeNotSpecifiedError

        raise InvalidPathError

    def post(self, path: str, query: str):
        path = urlparse(path)
        fpath = FPath(path.path)
        query = parse_query(query)

        if fpath.match("/currencies"):
            try:
                name, code, sign = query["name"], query["code"], query["sign"]
                return self.currencies_service.add(name, code, sign)

            except KeyError:
                raise QueryFieldNotSpecifiedError


        raise InvalidPathError

class DTOFactory:
    def __init__(self):
        self.service_client = ServiceClient()

    def get(self, request, urlpath: str, query: Optional[str] = None):
        service_client = self.service_client

        match request:
            case "GET":
                return service_client.get(urlpath)
            case "POST":
                return service_client.post(urlpath, query)



class Controller:
    def __init__(self):
        self.dto_factory = DTOFactory()


    def perform(self, request_method: str, urlpath: str, query: Optional[str] = None):
        response: HTTPResponseData = HTTPResponseData()
        try:

            dto: DTO = self.dto_factory.get(request_method, urlpath, query)

            response.code = 200
            response.add_header("Content-Type", "application/json")
            response.message = json.dumps(dto.tojson())


        except RequestException as err:
            response.code = err.RESPONSE_CODE
            response.add_header("Content-Type", "text/html")
            response.message = json.dumps({"message" : err.MESSAGE})

        content_len = str(len(response.message))
        response.add_header("Content_Length", content_len)

        return response








