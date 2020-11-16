import requests
import re

query = 'kaguya'
r = requests.get("https://guya.moe/api/get_all_series")
for t, item in r.json().items():
    if re.search(query, t, re.IGNORECASE):
        print(t)