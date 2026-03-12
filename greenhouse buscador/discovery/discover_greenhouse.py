import requests
import re

API_KEY = "e87768429bb37c0a0fc01891c22cf710"


def discover_companies():

    companies = set()

    for start in range(0, 200, 10):

        search_url = f"https://www.google.com/search?q=site:boards.greenhouse.io+jobs&start={start}"

        url = f"http://api.scraperapi.com/?api_key={API_KEY}&url={search_url}"

        try:
            r = requests.get(url, timeout=20)
            html = r.text
        except:
            continue

        tokens = re.findall(r"boards\.greenhouse\.io/([a-zA-Z0-9_-]+)", html)

        for t in tokens:
            companies.add(t.lower())

    return list(companies)