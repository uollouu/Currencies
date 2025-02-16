from abc import ABC, abstractmethod


class RequestException(ABC, Exception):
    @property
    @abstractmethod
    def RESPONSE_CODE(self):
        pass

    @property
    @abstractmethod
    def MESSAGE(self):
        pass

    def __init__(self, *args):
        super().__init__(*args)

class NotFoundError(RequestException):
    RESPONSE_CODE = 404
    MESSAGE = "Not found"


class CurrencyNotFoundError(RequestException):
    RESPONSE_CODE = 404
    MESSAGE = "Currency Not Found"



class CurrencyCodeNotSpecifiedError(RequestException):
    RESPONSE_CODE = 400
    MESSAGE = "Currency Code Not Specified"


class InvalidPathError(RequestException):
    RESPONSE_CODE = 400
    MESSAGE = "Invalid Path"


class ExchangeRateNotFoundError(RequestException):
    RESPONSE_CODE = 404
    MESSAGE = "Exchange Rate Not Found"

class ExchangeUnavailableError(RequestException):
    RESPONSE_CODE = 404
    MESSAGE = "Exchange Cannot be performed"

class QueryFieldNotSpecifiedError(RequestException):
    RESPONSE_CODE = 400
    MESSAGE = "Form field not specified"

class InvalidCurrencyCodeError(RequestException):
    RESPONSE_CODE = 400
    MESSAGE = "Currency code must be 3 characters long"

class ExchangeRateAlreadyExistsError(RequestException):
    RESPONSE_CODE = 409
    MESSAGE = "Exchange rate already exists"

class ForeignKeyError(Exception):
    def __init__(self):
        super().__init__()

class InvalidAmountError(RequestException):
    RESPONSE_CODE = 400
    MESSAGE = "Amount have to be a number"







