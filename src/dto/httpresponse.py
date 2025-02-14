from dataclasses import dataclass


@dataclass
class HTTPHeaderDTO:
    keyword: str
    value: str


class HTTPResponseData:
    def __init__(self):
        self.code: int = 500
        self.headers: list[HTTPHeaderDTO] = []
        self.message: str = ""

    def add_header(self, keyword: str, value: str) -> None:
        self.headers.append(HTTPHeaderDTO(keyword, value))




