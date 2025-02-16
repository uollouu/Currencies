from urllib.parse import parse_qs

def parse_query(query):
    qr = parse_qs(query)
    query_dict = {k: qr[k][0] for k in qr}

    return query_dict
