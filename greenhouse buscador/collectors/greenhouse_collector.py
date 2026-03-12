import requests
import pandas as pd


def collect_jobs(company):

    url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except:
        return pd.DataFrame()

    jobs = data.get("jobs", [])

    if not jobs:
        return pd.DataFrame()

    rows = []

    for j in jobs:

        rows.append({
            "empresa": company,
            "title": j.get("title", ""),
            "location": j.get("location", {}).get("name", ""),
            "updated_at": j.get("updated_at", ""),
            "url": j.get("absolute_url", "")
        })

    return pd.DataFrame(rows)