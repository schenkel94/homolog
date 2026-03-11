import os
import re
import time
import io
import urllib.parse
from typing import List, Dict, Optional, Tuple

import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup


SCRAPER_API_KEY = os.getenv("e87768429bb37c0a0fc01891c22cf710")

DEFAULT_EMPRESAS_FILE = "empresas.txt"

DATA_KEYWORDS = [
    "dados", "data", "analytics", "analyt", "bi", "business intelligence",
    "cientista", "cientista de dados", "data scientist",
    "analista", "analista de dados", "data analyst",
    "engenheiro", "engenheiro de dados", "data engineer",
    "machine learning", "ml", "ia", "ai",
    "estat", "stat", "produto dados", "growth analytics", "insights"
]

EXCLUDE_KEYWORDS = [
    "banc", "contáb", "finance", "fiscal", "juríd", "legal", "sales", "vendas",
    "suporte", "atendimento", "customer success", "cs", "marketing"
]


def build_scraperapi_url(target_url: str) -> str:
    encoded_url = urllib.parse.quote(target_url, safe="")
    scraper_url = (
        "http://api.scraperapi.com/?api_key=" + str(SCRAPER_API_KEY) +
        "&url=" + encoded_url
    )
    return scraper_url


def safe_text(el) -> str:
    if el is None:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())


def normalize_space(txt: str) -> str:
    return " ".join((txt or "").split()).strip()


def looks_like_job_url(url: str) -> bool:
    if not url:
        return False
    url_low = url.lower()
    if "inhire.app" not in url_low:
        return False
    if "/vagas" not in url_low:
        return False
    if url_low.rstrip("/").endswith("/vagas"):
        return False
    return True


def absolutize_url(base_url: str, href: str) -> str:
    if not href:
        return ""
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return base_url.rstrip("/") + href
    return base_url.rstrip("/") + "/" + href


def is_data_role(title: str) -> bool:
    t = (title or "").lower()
    has_data = any(k in t for k in DATA_KEYWORDS)
    has_excl = any(k in t for k in EXCLUDE_KEYWORDS)
    return bool(has_data) and not bool(has_excl)


def extract_location_from_card(card_text: str) -> str:
    txt = normalize_space(card_text)
    if not txt:
        return ""

    patterns = [
        r"(remoto|remote|híbrido|hybrid|presencial|on[-\s]?site)\b",
        r"\b(São Paulo|SP|Rio de Janeiro|RJ|Belo Horizonte|BH|Minas Gerais|MG|Curitiba|PR|Porto Alegre|RS|Recife|PE|Fortaleza|CE|Salvador|BA|Brasil)\b"
    ]

    for pat in patterns:
        m = re.search(pat, txt, flags=re.IGNORECASE)
        if m:
            return normalize_space(m.group(0))

    return ""


def try_extract_from_next_data(soup: BeautifulSoup, base_url: str, empresa: str) -> List[Dict]:
    results: List[Dict] = []
    script = soup.find("script", id="__NEXT_DATA__")
    if script is None:
        return results

    raw = script.get_text(strip=True)
    if not raw:
        return results

    try:
        import json
        data = json.loads(raw)
    except Exception:
        return results

    def walk(obj):
        if isinstance(obj, dict):
            for _, v in obj.items():
                yield from walk(v)
        elif isinstance(obj, list):
            for it in obj:
                yield from walk(it)
        else:
            return

    candidate_dicts = []
    def collect_dicts(obj):
        if isinstance(obj, dict):
            candidate_dicts.append(obj)
            for v in obj.values():
                collect_dicts(v)
        elif isinstance(obj, list):
            for it in obj:
                collect_dicts(it)

    collect_dicts(data)

    for d in candidate_dicts:
        title = ""
        link = ""
        location = ""

        for k in ["title", "name", "position", "jobTitle", "cargo"]:
            if k in d and isinstance(d.get(k), str):
                title = d.get(k)
                break

        for k in ["url", "link", "applyUrl", "jobUrl", "slug"]:
            if k in d and isinstance(d.get(k), str):
                link = d.get(k)
                break

        for k in ["location", "city", "place", "local", "workplace", "workModel"]:
            v = d.get(k)
            if isinstance(v, str):
                location = v
                break
            if isinstance(v, dict):
                loc_parts = []
                for kk in ["city", "state", "country", "name"]:
                    if isinstance(v.get(kk), str):
                        loc_parts.append(v.get(kk))
                if loc_parts:
                    location = ", ".join(loc_parts)
                    break

        title = normalize_space(title)
        location = normalize_space(location)

        if title and link:
            job_url = link
            if job_url and "inhire.app" not in job_url.lower():
                job_url = absolutize_url(base_url, job_url)

            if looks_like_job_url(job_url):
                results.append({
                    "empresa": empresa,
                    "vaga": title,
                    "local": location,
                    "link": job_url
                })

    dedup = {}
    for r in results:
        key = (r.get("empresa", ""), r.get("vaga", ""), r.get("link", ""))
        dedup[key] = r

    return list(dedup.values())


def extract_jobs_from_html(html: str, empresa: str, target_url: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    base_url = "https://" + empresa + ".inhire.app"

    jobs: List[Dict] = []

    next_jobs = try_extract_from_next_data(soup, base_url, empresa)
    if next_jobs:
        return next_jobs

    anchors = soup.find_all("a", href=True)
    for a in anchors:
        href = a.get("href", "")
        job_url = absolutize_url(base_url, href)
        if not looks_like_job_url(job_url):
            continue

        title = safe_text(a)
        if not title or len(title) < 3:
            title = safe_text(a.find(["h1", "h2", "h3", "h4", "span", "div"]))

        card = a
        for _ in range(4):
            if card is None:
                break
            if card.name in ["li", "article", "section", "div"]:
                break
            card = card.parent

        card_text = safe_text(card) if card is not None else safe_text(a)
        location = extract_location_from_card(card_text)

        title = normalize_space(title)
        if title:
            jobs.append({
                "empresa": empresa,
                "vaga": title,
                "local": location,
                "link": job_url
            })

    if not jobs:
        for tag in soup.find_all(["li", "article", "section", "div"]):
            tag_text = safe_text(tag)
            if not tag_text:
                continue
            a = tag.find("a", href=True)
            if a is None:
                continue
            job_url = absolutize_url(base_url, a.get("href", ""))
            if not looks_like_job_url(job_url):
                continue

            title = safe_text(tag.find(["h1", "h2", "h3", "h4"])) or safe_text(a)
            title = normalize_space(title)
            if not title:
                continue

            location = extract_location_from_card(tag_text)
            jobs.append({
                "empresa": empresa,
                "vaga": title,
                "local": location,
                "link": job_url
            })

    dedup = {}
    for r in jobs:
        key = (r.get("empresa", ""), r.get("vaga", ""), r.get("link", ""))
        dedup[key] = r
    return list(dedup.values())


def fetch_html_via_scraperapi(target_url: str, timeout_s: int = 40) -> Tuple[Optional[str], Optional[str]]:
    if not SCRAPER_API_KEY:
        return None, "SCRAPER_API_KEY não está definida no ambiente."

    scraper_url = build_scraperapi_url(target_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; InHireJobsRadar/1.0; +https://julius.ai)"
    }

    try:
        resp = requests.get(scraper_url, headers=headers, timeout=timeout_s)
    except requests.RequestException as e:
        return None, "Erro de rede: " + str(e)

    if resp.status_code != 200:
        return None, "HTTP " + str(resp.status_code)

    txt = resp.text or ""
    if len(txt.strip()) < 200:
        return None, "HTML muito curto (pode ter bloqueio ou erro)."

    return txt, None


def load_empresas(path: str) -> List[str]:
    if not os.path.exists(path):
        return ["sympla", "olist", "cora", "pipefy"]

    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    empresas = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        empresas.append(line)

    return empresas


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="vagas")
        workbook = writer.book
        worksheet = writer.sheets["vagas"]
        worksheet.set_column(0, 0, 18)
        worksheet.set_column(1, 1, 45)
        worksheet.set_column(2, 2, 18)
        worksheet.set_column(3, 3, 70)
    return output.getvalue()


st.set_page_config(page_title="Radar de Vagas de Dados em Startups", layout="wide")
st.title("Radar de Vagas de Dados em Startups")

with st.expander("Configuração", expanded=False):
    st.write("A lista de empresas é lida de `empresas.txt` (um slug por linha).")
    st.write("A ScraperAPI Key deve estar no ambiente como `SCRAPER_API_KEY`.")
    st.code("export SCRAPER_API_KEY=SEU_TOKEN_AQUI")

empresas_list = load_empresas(DEFAULT_EMPRESAS_FILE)

col_a, col_b, col_c = st.columns([2, 2, 2])
with col_a:
    empresa_filter = st.multiselect("Filtro por empresa", options=sorted(empresas_list), default=[])
with col_b:
    cargo_filter = st.text_input("Filtro por palavra no cargo", value="")
with col_c:
    timeout_s = st.number_input("Timeout da request (s)", min_value=10, max_value=120, value=40, step=5)

buscar = st.button("Buscar vagas", type="primary")

if buscar:
    progress = st.progress(0)
    status_box = st.empty()

    all_rows: List[Dict] = []
    errors: List[Dict] = []

    total = len(empresas_list)
    for idx, empresa in enumerate(empresas_list):
        target_url = "https://" + empresa + ".inhire.app/vagas"
        status_box.write("Buscando: " + empresa + "  " + target_url)

        html, err = fetch_html_via_scraperapi(target_url, timeout_s=int(timeout_s))
        if err:
            errors.append({"empresa": empresa, "erro": err})
            progress.progress(int(((idx + 1) / max(total, 1)) * 100))
            time.sleep(0.2)
            continue

        try:
            jobs = extract_jobs_from_html(html, empresa=empresa, target_url=target_url)
        except Exception as e:
            errors.append({"empresa": empresa, "erro": "Falha no parsing: " + str(e)})
            progress.progress(int(((idx + 1) / max(total, 1)) * 100))
            time.sleep(0.2)
            continue

        if not jobs:
            progress.progress(int(((idx + 1) / max(total, 1)) * 100))
            time.sleep(0.2)
            continue

        for r in jobs:
            if is_data_role(r.get("vaga", "")):
                all_rows.append(r)

        progress.progress(int(((idx + 1) / max(total, 1)) * 100))
        time.sleep(0.2)

    status_box.write("Concluído.")

    if not all_rows:
        st.warning("Nenhuma vaga de dados encontrada nas empresas listadas.")
    else:
        df = pd.DataFrame(all_rows)
        df = df.drop_duplicates(subset=["empresa", "vaga", "link"]).copy()
        df = df.sort_values(["empresa", "vaga"], ascending=[True, True]).reset_index(drop=True)

        st.subheader("Resumo")
        st.metric("Total de vagas de dados encontradas", int(df.shape[0]))

        df_view = df.copy()

        if empresa_filter:
            df_view = df_view[df_view["empresa"].isin(empresa_filter)].copy()

        if cargo_filter.strip():
            q = cargo_filter.strip().lower()
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
