import os
from adaptix import retort
from urllib.parse import urlparse, parse_qs
t = parse_qs(urlparse("/exchange").query)
if t :
    print(1)

