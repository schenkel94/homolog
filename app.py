import os
import re
import time
import io
import urllib.parse
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# --- Configurações ---
SCRAPER_API_KEY = "e87768429bb37c0a0fc01891c22cf710"  # TOKEN SIMBÓLICO
BASE_URL_TEMPLATE = "https://{}.inhire.app/vagas"
DATA_JOB_KEYWORDS = [
    "data", "dados", "cientista de dados", "engenheiro de dados",
    "analista de dados", "machine learning", "inteligência artificial",
    "business intelligence", "bi"
]
REQUEST_TIMEOUT = 15  # segundos

# --- Funções Auxiliares ---
@st.cache_data
def get_company_list(filename="empresas.txt") -> List[str]:
    if not os.path.exists(filename):
        st.error(f"Arquivo '{filename}' não encontrado. Crie-o com uma lista de empresas.")
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_page_content(company_name: str, api_key: str) -> str | None:
    """Busca o conteúdo da página usando ScraperAPI com renderização JS."""
    target_url = BASE_URL_TEMPLATE.format(company_name)
    scraper_url = (
        f"http://api.scraperapi.com/?api_key={api_key}&render=true&url={urllib.parse.quote(target_url)}"
    )
    try:
        response = requests.get(scraper_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar {target_url} para {company_name}: {e}")
        return None

def parse_inhire_page(html_content: str, company_name: str) -> List[Dict[str, str]]:
    """Analisa o HTML renderizado para extrair vagas."""
    soup = BeautifulSoup(html_content, "html.parser")
    jobs = []

    # Procura o JSON embutido
    next_data_script = soup.find("script", {"id": "__NEXT_DATA__"})
    if next_data_script:
        try:
            import json
            data = json.loads(next_data_script.string)
            st.json(data)  # Mostra a árvore completa para depuração

            # Ajuste conforme a estrutura real
            page_props = data.get("props", {}).get("pageProps", {})
            if "jobs" in page_props:
                for job_data in page_props["jobs"]:
                    job_title = job_data.get("title")
                    job_location = job_data.get("location", "Não informado")
                    job_link = job_data.get("url") or job_data.get("link")
                    if job_title and job_link:
                        jobs.append({
                            "empresa": company_name,
                            "vaga": job_title,
                            "local": job_location,
                            "link": job_link
                        })
        except Exception as e:
            st.warning(f"Falha ao interpretar JSON: {e}")

    # Fallback heurístico
    if not jobs:
        job_elements = soup.find_all("a", href=re.compile(r"/vaga/", re.IGNORECASE))
        for element in job_elements:
            job_title = element.get_text(strip=True)
            job_link = urllib.parse.urljoin(BASE_URL_TEMPLATE.format(company_name), element["href"])
            if job_title and job_link:
                jobs.append({
                    "empresa": company_name,
                    "vaga": job_title,
                    "local": "Não informado",
                    "link": job_link
                })
    return jobs

def filter_jobs_by_keywords(jobs: List[Dict[str, str]], keywords: List[str]) -> List[Dict[str, str]]:
    filtered_jobs = []
    for job in jobs:
        job_text = (job["vaga"] + " " + job["local"]).lower()
        if any(keyword.lower() in job_text for keyword in keywords):
            filtered_jobs.append(job)
    return filtered_jobs

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vagas de Dados')
    return output.getvalue()

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title("Radar de Vagas de Dados em Startups")

company_list = get_company_list()
if not company_list:
    st.stop()

st.sidebar.header("Filtros")
selected_company = st.sidebar.selectbox("Filtrar por Empresa", ["Todas"] + company_list)
job_title_query = st.sidebar.text_input("Filtrar por Título da Vaga (palavra-chave)")

if st.button("Buscar vagas"):
    all_jobs = []
    errors = []
    html_contents_for_debug = {}

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, company in enumerate(company_list):
        status_text.text(f"Buscando vagas em {company}...")
        html_content = fetch_page_content(company, SCRAPER_API_KEY)

        if html_content:
            html_contents_for_debug[company] = html_content
            jobs_found = parse_inhire_page(html_content, company)
            if jobs_found:
                all_jobs.extend(jobs_found)
            else:
                errors.append({"empresa": company, "status": "Nenhuma vaga encontrada ou parsing falhou."})
        else:
            errors.append({"empresa": company, "status": "Falha ao buscar conteúdo da página."})

        progress_bar.progress((i + 1) / len(company_list))
        time.sleep(0.5)

    status_text.text("Busca concluída!")
    progress_bar.empty()

    if html_contents_for_debug:
        with st.expander("HTMLs Brutos Recebidos (para depuração)", expanded=False):
            for company, html in html_contents_for_debug.items():
                st.subheader(f"HTML de {company}")
                st.text_area(f"HTML para {company}", html, height=300)

    if all_jobs:
        df = pd.DataFrame(all_jobs)
        df_filtered_by_keywords = filter_jobs_by_keywords(df.to_dict('records'), DATA_JOB_KEYWORDS)
        df_final = pd.DataFrame(df_filtered_by_keywords)

        st.subheader(f"Total de Vagas de Dados Encontradas: {len(df_final)}")

        df_view = df_final.copy()
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
