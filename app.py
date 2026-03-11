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

def fetch_page_content(url: str) -> str | None:
    """
    Faz a requisição HTTP usando ScraperAPI e retorna o conteúdo HTML.
    Imprime o HTML para depuração.
    """
    if not SCRAPER_API_KEY:
        st.error("SCRAPER_API_KEY não está definida. Por favor, defina-a.")
        return None

    encoded_url = urllib.parse.quote(url)
    scraper_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={encoded_url}"

    try:
        response = requests.get(scraper_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)
        html_content = response.text

        # --- DEBUG: Imprime o HTML recebido ---
        print(f"--- HTML recebido para {url} ---")
        print(html_content[:2000]) # Imprime os primeiros 2000 caracteres para não sobrecarregar
        print(f"--- Fim do HTML para {url} ---")
        # --- FIM DEBUG ---

        return html_content
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar {url} via ScraperAPI: {e}")
        return None

def parse_inhire_page(html_content: str, company_name: str) -> List[Dict[str, str]]:
    """
    Analisa o HTML de uma página InHire e extrai as vagas.
    Esta função é uma heurística e pode precisar de ajustes com o HTML real.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    jobs = []

    # Tentativa 1: Procurar por links de vagas ou cards comuns
    # InHire geralmente usa divs com classes específicas ou links para as vagas.
    # Vamos procurar por <a> tags que contenham "vaga" ou "job" no href ou texto,
    # ou divs que pareçam cards de vaga.

    # Heurística 1: Links que parecem vagas
    # Ex: <a href="/vagas/nome-da-vaga" ...>
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/vagas/" in href and a_tag.text.strip():
            job_title = a_tag.text.strip()
            # Tenta encontrar o local próximo ao link
            location_element = a_tag.find_next_sibling("span") or a_tag.find_next("div", class_=re.compile("location|local"))
            location = location_element.text.strip() if location_element else "Não informado"
            full_link = urllib.parse.urljoin(BASE_URL_TEMPLATE.format(company_name), href)
            jobs.append({
                "empresa": company_name,
                "vaga": job_title,
                "local": location,
                "link": full_link
            })

    # Heurística 2: Cards de vaga (divs com títulos e detalhes)
    # Esta é uma suposição comum para ATS.
    # Vamos procurar por divs que contenham um título (h2, h3) e talvez um link.
    # Classes comuns para cards de vaga: "job-card", "job-listing", "vacancy-item"
    for job_card in soup.find_all("div", class_=re.compile("job-card|job-listing|vacancy-item|vaga-item", re.IGNORECASE)):
        job_title_elem = job_card.find(["h2", "h3", "span"], class_=re.compile("title|name|vaga", re.IGNORECASE))
        job_title = job_title_elem.text.strip() if job_title_elem else "Título não encontrado"

        location_elem = job_card.find("span", class_=re.compile("location|local", re.IGNORECASE))
        location = location_elem.text.strip() if location_elem else "Não informado"

        link_elem = job_card.find("a", href=True)
        link = urllib.parse.urljoin(BASE_URL_TEMPLATE.format(company_name), link_elem["href"]) if link_elem else BASE_URL_TEMPLATE.format(company_name)

        if job_title != "Título não encontrado": # Evita adicionar cards vazios
            jobs.append({
                "empresa": company_name,
                "vaga": job_title,
                "local": location,
                "link": link
            })

    # Heurística 3: JSON-LD (Structured Data) - muito comum em páginas de vagas
    # <script type="application/ld+json">
    for script_tag in soup.find_all("script", type="application/ld+json"):
        try:
            import json
            data = json.loads(script_tag.string)
            if isinstance(data, dict) and data.get("@type") == "JobPosting":
                jobs.append({
                    "empresa": company_name,
                    "vaga": data.get("title", "Título não encontrado"),
                    "local": data.get("jobLocation", {}).get("address", {}).get("addressLocality", "Não informado"),
                    "link": data.get("url", BASE_URL_TEMPLATE.format(company_name))
                })
            elif isinstance(data, list): # Às vezes é uma lista de objetos JSON-LD
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "JobPosting":
                        jobs.append({
                            "empresa": company_name,
                            "vaga": item.get("title", "Título não encontrado"),
                            "local": item.get("jobLocation", {}).get("address", {}).get("addressLocality", "Não informado"),
                            "link": item.get("url", BASE_URL_TEMPLATE.format(company_name))
                        })
        except json.JSONDecodeError:
            continue # Ignora scripts que não são JSON válidos

    # Remove duplicatas se as heurísticas encontrarem a mesma vaga
    unique_jobs = []
    seen_links = set()
    for job in jobs:
        if job["link"] not in seen_links:
            unique_jobs.append(job)
            seen_links.add(job["link"])

    return unique_jobs


def filter_data_jobs(jobs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Filtra as vagas para incluir apenas as relacionadas à área de dados."""
    data_jobs = []
    for job in jobs:
        job_title_lower = job["vaga"].lower()
        if any(keyword in job_title_lower for keyword in DATA_JOB_KEYWORDS):
            data_jobs.append(job)
    return data_jobs

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Converte um DataFrame pandas para um arquivo Excel em bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Vagas de Dados')
    processed_data = output.getvalue()
    return processed_data

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title("Radar de Vagas de Dados em Startups")

company_list = get_company_list()

if not company_list:
    st.warning("Por favor, crie o arquivo 'empresas.txt' com uma lista de empresas (uma por linha).")
    st.stop()

if st.button("Buscar vagas"):
    all_jobs: List[Dict[str, str]] = []
    errors: List[Dict[str, str]] = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, company in enumerate(company_list):
        status_text.text(f"Buscando vagas em: {company} ({i+1}/{len(company_list)})")
        url = BASE_URL_TEMPLATE.format(company)
        html_content = fetch_page_content(url)

        if html_content:
            try:
                company_jobs = parse_inhire_page(html_content, company)
                if company_jobs:
                    all_jobs.extend(company_jobs)
                else:
                    errors.append({"empresa": company, "status": "Nenhuma vaga encontrada ou parsing falhou."})
            except Exception as e:
                errors.append({"empresa": company, "status": f"Erro de parsing: {e}"})
        else:
            errors.append({"empresa": company, "status": "Falha ao buscar conteúdo da página."})

        progress_bar.progress((i + 1) / len(company_list))
        time.sleep(0.5) # Pequeno delay para não sobrecarregar

    status_text.text("Busca concluída!")
    progress_bar.empty()

    if not all_jobs:
        st.warning("Nenhuma vaga de dados encontrada em nenhuma das empresas listadas.")
        if errors:
            with st.expander("Detalhes dos erros/empresas ignoradas", expanded=False):
                st.dataframe(pd.DataFrame(errors), use_container_width=True, hide_index=True)
        st.stop()

    df_all_jobs = pd.DataFrame(all_jobs)
    df_data_jobs = pd.DataFrame(filter_data_jobs(all_jobs))

    st.success(f"Total de vagas encontradas (todas as áreas): {len(df_all_jobs)}")
    st.success(f"Total de vagas de dados encontradas: {len(df_data_jobs)}")

    if not df_data_jobs.empty:
        st.subheader("Filtros")
        col1, col2 = st.columns(2)
        with col1:
            selected_company = st.selectbox("Filtrar por empresa:", ["Todas"] + sorted(df_data_jobs["empresa"].unique().tolist()))
        with col2:
            job_title_query = st.text_input("Filtrar por palavra no cargo:")

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

