import re
import urllib.parse
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL_TEMPLATE = "https://{}.inhire.app/vagas"
KEYWORDS = ["analista de dados", "data analyst", "analista de negocios"]

def fetch_page(company):
    url = BASE_URL_TEMPLATE.format(company)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()
    return html

def parse_jobs(html, company):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for link in soup.find_all("a", href=True):
        if link["href"].startswith("vagas/"):
            title = link.get_text(strip=True)
            url = urllib.parse.urljoin(BASE_URL_TEMPLATE.format(company), link["href"])
            text_lower = title.lower()
            # filtro por keywords
            if any(k in text_lower for k in KEYWORDS):
                jobs.append({
                    "empresa": company,
                    "nome_vaga": title,
                    "localidade": extract_location(title),
                    "link": url,
                    "data_etl": pd.Timestamp.now().strftime("%Y-%m-%d")
                })
    return jobs

def extract_location(title: str) -> str:
    # tenta extrair localidade depois de "|"
    parts = title.split("|")
    if len(parts) > 1:
        return parts[-1].strip()
    return "Não informado"

def main():
    with open("companies.txt", "r", encoding="utf-8") as f:
        companies = [line.strip() for line in f if line.strip()]

    all_jobs = []
    for c in companies:
        try:
            print(f"Buscando {c}...")
            html = fetch_page(c)
            jobs = parse_jobs(html, c)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"Erro em {c}: {e}")

    df = pd.DataFrame(all_jobs)
    print(df)

    # salva em CSV e Excel
    df.to_csv("vagas.csv", index=False, encoding="utf-8")
    df.to_excel("vagas.xlsx", index=False)

if __name__ == "__main__":
    main()
