from urllib.parse import urlparse, parse_qs
from typing import Optional
import json

from src.utils.exceptions import (RequestException,
                                  CurrencyCodeNotSpecifiedError,
                                  QueryFieldNotSpecifiedError,
                                  WrongCurrencyCodeError,
                                  InvalidPathError)
from src.services.service import CurrenciesService, ExchangeRatesService, ExchangeService
from src.dto.httpresponse import HTTPResponseData
from src.dto.basedto import DTO
from src.utils.singleton import Singleton
from src.utils.fpath import FPath


class DTOFactory(Singleton):
    def __init__(self):
        self.currencies_service = CurrenciesService()
        self.exchange_rates_service = ExchangeRatesService()
        self.exchange_service = ExchangeService()

    def get(self, path: str, query: Optional = None) -> DTO:
        fpath = FPath(path)

        if fpath.match("/currencies"):
            return self.currencies_service.get_all()

        if fpath.match("/currency/*"):
            currency_code = fpath[1]
            return self.currencies_service.get_one(currency_code=currency_code)

        if fpath.match("/currency"):
            raise CurrencyCodeNotSpecifiedError

        if fpath.match("/exchangeRates"):
            return self.exchange_rates_service.get_all()

        if fpath.match("/exchangeRate/*"):
            currencies_codes = fpath[1]

            if len(currencies_codes) != 6:
                raise WrongCurrencyCodeError

            currency_code1, currency_code2 = currencies_codes[:3], currencies_codes[3:]

            return self.exchange_rates_service.get_one(currency_code1, currency_code2)

        if fpath.match("/exchange"):
            quer = parse_qs(query)
            params = {k: quer[k][0] for k in quer}
            try:
                base_currency_code = params["from"]
                target_currency_code = params["to"]
                amount = params["amount"]

                self.exchange_service.get(base_currency_code,
                                          target_currency_code,
                                          amount)
            except KeyError:
                raise QueryFieldNotSpecifiedError

        raise InvalidPathError

    def post(self, path: str, query):
        fpath = FPath(path)
        quer = parse_qs(query)
        params = {k: quer[k][0] for k in quer}

        if fpath.match("/currencies"):
            try:
                name, code, sign = params["name"], params["code"], params["sign"]
                return self.currencies_service.add(name, code, sign)

            except KeyError:
                raise QueryFieldNotSpecifiedError


        raise InvalidPathError


class Controller:
    def __init__(self):
        self.dto_factory = DTOFactory()

    def get(self, urlpath):
        response: HTTPResponseData = HTTPResponseData()
        try:
            urlpath = urlparse(urlpath)
            path = urlpath.path
            query = urlpath.query
            dto: DTO = self.dto_factory.get(urlpath.path, query)

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








