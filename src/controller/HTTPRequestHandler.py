from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from src.controller.controller import Controller

from src.dto.httpresponse import HTTPResponseData, HTTPHeaderDTO
import json

class HTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        self.controller = Controller()
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        host, port = self.server.server_address
        url = f"http://{host}:{port}{self.path}"
        print({i: k for i, k in parse_qs(self.path)})
        response: HTTPResponseData = self.controller.get(url)

        self.send_response(response.code)
        self.__send_headers(response.headers)
        self.wfile.write(response.message.encode('utf-8'))



    def __send_headers(self, headers: list[HTTPHeaderDTO]):
        for header in headers:
            self.send_header(header.keyword, header.value)
        self.end_headers()










httpd = HTTPServer(('',8000), HTTPRequestHandler)
httpd.serve_forever()