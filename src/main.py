import sqlite3

import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

def build_answer():
    con = sqlite3.connect("db/currency_exchange.db")
    cur = con.cursor()
    res = cur.execute("select * from currencies")
    columns_names = [i[0] for i in res.description]
    strokes = res.fetchall()
    ar = []
    for i in range(len(strokes)):
        ar.append({})
        for j in range(len(columns_names)):
            ar[-1][columns_names[j]] = strokes[i][j]
    return json.dumps(ar)

def db_get(currency_code):
    con = sqlite3.connect("db/currency_exchange.db")
    cur = con.cursor()
    res = cur.execute(f"""select * from currencies where
                      code = '{currency_code}'""")

    stroke = res.fetchone()
    if stroke is None : return
    columns_names = [i[0] for i in res.description]
    ta = {}
    for j in range(len(columns_names)):
        ta[columns_names[j]] = stroke[j]

    return json.dumps(ta)


class ModifiedRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):

        path = [i for i in self.path.split("/") if i.strip()]


        if path == ['currencies']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(build_answer(),'utf-8'))
        elif path[0] == 'currencies' and len(path) == 2:
            currency_code = path[1]
            currency = db_get(currency_code)

            if currency is None:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(bytes("no", 'utf-8'))
                return
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(bytes(currency,'utf-8'))

        else:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("none", 'utf-8'))




httpd = HTTPServer(('',8000), ModifiedRequestHandler)
httpd.serve_forever()