from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from src.controller.controller import Controller

from src.dto.httpresponse import HTTPResponseData, HTTPHeaderDTO
import json

class HTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        self.controller = Controller()
        super().__init__(*args, **kwargs)

    def _send_http_response(self, response: HTTPResponseData) -> None:

        self.send_response(response.code)
        self._send_headers(response.headers)
        self.wfile.write(response.message.encode('utf-8'))

    def do_GET(self) -> None:
        response: HTTPResponseData = self.controller.perform("GET", self.path)
        self._send_http_response(response)

    def do_POST(self) -> None:
        content_len = int(self.headers["Content-Length"])
        query = self.rfile.read(content_len).decode('UTF-8')

        response: HTTPResponseData = self.controller.perform("POST",
                                                             self.path, query)
        self._send_http_response(response)


    def _send_headers(self, headers: list[HTTPHeaderDTO]):
        for header in headers:
            self.send_header(header.keyword, header.value)
        self.end_headers()










httpd = HTTPServer(('',8000), HTTPRequestHandler)
httpd.serve_forever()