import os
import re
import time
import io
import urllib.parse
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# --- Configurações ---
# Substitua esta linha pelo seu token real quando for para produção,
# ou use variáveis de ambiente como SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
SCRAPER_API_KEY = "e87768429bb37c0a0fc01891c22cf710" # TOKEN SIMBÓLICO FORNECIDO PELO USUÁRIO

BASE_URL_TEMPLATE = "https://{}.inhire.app/vagas"
DATA_JOB_KEYWORDS = ["data", "dados", "cientista de dados", "engenheiro de dados", "analista de dados", "machine learning", "inteligência artificial", "business intelligence", "bi"]
REQUEST_TIMEOUT = 10 # segundos

# --- Funções Auxiliares ---
@st.cache_data
def get_company_list(filename="empresas.txt") -> List[str]:
    """Lê a lista de empresas de um arquivo."""
    if not os.path.exists(filename):
        st.error(f"Arquivo '{filename}' não encontrado. Crie um arquivo com uma empresa por linha.")
        return []
    with open(filename, "r", encoding="utf-8") as f:
        companies = [line.strip() for line in f if line.strip()]
    return companies

def fetch_page_with_scraperapi(target_url: str) -> str | None:
    """Faz a requisição da página usando ScraperAPI."""
    if not SCRAPER_API_KEY:
        st.error("SCRAPER_API_KEY não está definida. Por favor, configure-a.")
        return None

    encoded_target_url = urllib.parse.quote(target_url)
    scraper_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_target_url}"

    try:
        response = requests.get(scraper_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # Levanta HTTPError para códigos de status de erro (4xx ou 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        st.warning(f"Erro ao buscar {target_url} via ScraperAPI: {e}")
        return None

def parse_inhire_page(html_content: str, company_name: str) -> List[Dict[str, str]]:
    """
    Analisa o HTML da página InHire para extrair vagas.
    Esta função usa heurísticas e um fallback para JSON embutido.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    jobs = []

    # Heurística 1: Procurar por links de vagas ou cards comuns
    # Este é um exemplo genérico. O ideal é ajustar com o HTML real.
    job_elements = soup.find_all(["a", "div"], class_=re.compile(r"job|vaga|card", re.I))

    for element in job_elements:
        title = ""
        link = ""
        location = ""

        # Tenta extrair título
        title_tag = element.find(["h2", "h3", "span"], class_=re.compile(r"title|cargo|position", re.I))
        if title_tag:
            title = title_tag.get_text(strip=True)
        elif element.name == "a" and element.get("title"):
            title = element.get("title")
        elif element.name == "a" and element.get_text(strip=True):
            title = element.get_text(strip=True)

        # Tenta extrair link
        if element.name == "a" and element.get("href"):
            link = urllib.parse.urljoin(BASE_URL_TEMPLATE.format(company_name), element.get("href"))
        else:
            link_tag = element.find("a", href=True)
            if link_tag:
                link = urllib.parse.urljoin(BASE_URL_TEMPLATE.format(company_name), link_tag.get("href"))

        # Tenta extrair localização (exemplo genérico)
        location_tag = element.find(["span", "div"], class_=re.compile(r"location|local|city", re.I))
        if location_tag:
            location = location_tag.get_text(strip=True)

        if title and link: # Apenas adiciona se tiver título e link
            jobs.append({
                "empresa": company_name,
                "vaga": title,
                "local": location if location else "Não informado",
                "link": link
            })

    # Heurística 2: Fallback para dados JSON embutidos (ex: __NEXT_DATA__ ou application/ld+json)
    # Muitos sites modernos usam isso para renderização no lado do cliente.
    script_tags = soup.find_all("script", type="application/ld+json")
    script_tags.extend(soup.find_all("script", id="__NEXT_DATA__"))

    for script in script_tags:
        try:
            import json
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                jobs.append({
                    "empresa": company_name,
                    "vaga": data.get("title", ""),
                    "local": data.get("jobLocation", {}).get("address", {}).get("addressLocality", "Não informado"),
                    "link": data.get("url", "")
                })
            elif isinstance(data, dict) and "props" in data and "pageProps" in data["props"] and "jobs" in data["props"]["pageProps"]:
                # Exemplo de extração de __NEXT_DATA__ (pode variar muito)
                for job_data in data["props"]["pageProps"]["jobs"]:
                    jobs.append({
                        "empresa": company_name,
                        "vaga": job_data.get("title", ""),
                        "local": job_data.get("location", "Não informado"),
                        "link": job_data.get("url", "")
                    })
        except (json.JSONDecodeError, TypeError):
            continue # Ignora scripts que não são JSON ou não têm a estrutura esperada

    return jobs

def filter_data_jobs(jobs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Filtra vagas que contêm palavras-chave relacionadas a dados."""
    filtered_jobs = []
    for job in jobs:
        job_title_lower = job["vaga"].lower()
        if any(keyword in job_title_lower for keyword in DATA_JOB_KEYWORDS):
            filtered_jobs.append(job)
    return filtered_jobs

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Converte um DataFrame para bytes de um arquivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vagas de Dados')
    processed_data = output.getvalue()
    return processed_data

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title("Radar de Vagas de Dados em Startups")

companies = get_company_list()

if not companies:
    st.stop()

if st.button("Buscar vagas"):
    all_jobs: List[Dict[str, str]] = []
    errors: List[Dict[str, str]] = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, company in enumerate(companies):
        status_text.text(f"Buscando vagas em: {company} ({i+1}/{len(companies)})")
        target_url = BASE_URL_TEMPLATE.format(company)
        html_content = fetch_page_with_scraperapi(target_url)

        if html_content:
            company_jobs = parse_inhire_page(html_content, company)
            if company_jobs:
                all_jobs.extend(company_jobs)
            else:
                errors.append({"empresa": company, "status": "Nenhuma vaga encontrada ou erro de parsing."})
        else:
            errors.append({"empresa": company, "status": "Erro ao acessar a página."})

        progress_bar.progress((i + 1) / len(companies))
        time.sleep(0.1) # Pequeno delay para evitar sobrecarga e mostrar progresso

    status_text.text("Busca concluída!")
    progress_bar.empty()

    if not all_jobs:
        st.warning("Nenhuma vaga encontrada nas empresas listadas.")
    else:
        df_all_jobs = pd.DataFrame(all_jobs)
        df_data_jobs = pd.DataFrame(filter_data_jobs(all_jobs))

        st.subheader(f"Total de vagas de dados encontradas: {len(df_data_jobs)}")

        # --- Filtros ---
        st.sidebar.header("Filtros")

        # Filtro por empresa
        unique_companies = ["Todas"] + sorted(df_data_jobs["empresa"].unique().tolist())
        selected_company = st.sidebar.selectbox("Filtrar por empresa:", unique_companies)

        # Filtro por palavra no cargo
        job_title_query = st.sidebar.text_input("Filtrar por palavra no cargo:", "").strip()

        df_view = df_data_jobs.copy()

        if selected_company != "Todas":
            df_view = df_view[df_view["empresa"] == selected_company].copy()

        if job_title_query:
            q = job_title_query.lower().strip()
            df_view = df_view[df_view["vaga"].str.lower().str.contains(re.escape(q), na=False)].copy()

        st.subheader("Vagas")
        st.dataframe(df_view, use_container_width=True, hide_index=True)

        excel_bytes = to_excel_bytes(df_view)
        st.download_button(
            label="Baixar Excel",
            data=excel_bytes,
            file_name="vagas_dados_inhire.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if errors:
        with st.expander("Erros e empresas ignoradas", expanded=False):
            st.dataframe(pd.DataFrame(errors), use_container_width=True, hide_index=True)
else:
    st.info("Clique em **Buscar vagas** para iniciar.")
