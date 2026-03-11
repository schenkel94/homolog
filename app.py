import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import time
import re

st.set_page_config(
    page_title="Radar de Vagas de Dados em Startups",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

KEYWORDS_DATA = [
    "data", "dados", "data analyst", "data engineer", "analytics", "business intelligence",
    "bi", "machine learning", "ml", "ai", "analista de dados", "cientista de dados",
    "data science", "engenheiro de dados", "business analyst", "analytic", "devops"
]

KEYWORDS_REMOTE = ["remote", "remoto", "anywhere", "brazil remote", "home office"]

def load_companies():
    try:
        with open("empresas.txt", "r", encoding="utf-8") as f:
            content = f.read()
            companies = [c.strip().strip('"').strip(',') for c in content.split('\n')]
            companies = [c for c in companies if c and not c.startswith('#')]
            return companies
    except FileNotFoundError:
        st.error("❌ Arquivo 'empresas.txt' não encontrado!")
        return []

def scrape_jobs(company_name):
    """Faz scrape das vagas usando múltiplas estratégias"""
    url = f"https://{company_name}.inhire.app/vagas"
    
    try:
        # Tenta com headers realistas
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        jobs = []
        
        # **Estratégia 1: Encontra pela classe css-1klv894 e css-uormui**
        job_items = soup.find_all('li', class_='css-1klv894')
        
        for item in job_items:
            try:
                # Encontra o link
                link_elem = item.find('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                link = link_elem.get('href', '')
                
                # Encontra o título pela classe css-uormui
                title_elem = item.find('div', class_='css-uormui')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                if not title or not link:
                    continue
                
                # Extrai localidade
                localidade = ""
                if " | " in title:
                    parts = title.split(" | ")
                    if len(parts) > 1:
                        localidade = parts[-1].strip()
                
                # Garante URL absoluta
                if not link.startswith('http'):
                    link = f"https://{company_name}.inhire.app{link}"
                
                jobs.append({
                    'empresa': company_name,
                    'titulo': title,
                    'localidade': localidade,
                    'link': link
                })
            except Exception as e:
                continue
        
        # **Estratégia 2: Se não encontrou, tenta regex no HTML bruto**
        if not jobs:
            html_text = str(soup)
            # Procura por padrões como "Analista de dados sênior | Remoto"
            pattern = r'<div[^>]*class="css-uormui[^>]*>([^<]+)</div>'
            matches = re.findall(pattern, html_text)
            
            for title in matches:
                title = title.strip()
                if title and len(title) > 3:
                    localidade = ""
                    if " | " in title:
                        parts = title.split(" | ")
                        if len(parts) > 1:
                            localidade = parts[-1].strip()
                    
                    jobs.append({
                        'empresa': company_name,
                        'titulo': title,
                        'localidade': localidade,
                        'link': url  # Link genérico se não encontrar específico
                    })
        
        return jobs
        
    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.ConnectionError:
        return []
    except Exception as e:
        return []

def is_data_job(job_title):
    """Verifica se a vaga é de dados"""
    title_lower = job_title.lower()
    return any(keyword in title_lower for keyword in KEYWORDS_DATA)

def is_remote_job(localidade):
    """Verifica se é remota"""
    if not localidade:
        return False
    localidade_lower = localidade.lower()
    return any(keyword in localidade_lower for keyword in KEYWORDS_REMOTE)

def filter_jobs(all_jobs, filter_company=None, filter_keyword=None):
    """Filtra vagas"""
    filtered = all_jobs.copy()
    
    if filter_company and filter_company != "Todas":
        filtered = filtered[filtered['empresa'] == filter_company]
    
    if filter_keyword and filter_keyword.strip():
        keyword_lower = filter_keyword.strip().lower()
        filtered = filtered[
            filtered['titulo'].str.lower().str.contains(keyword_lower, na=False)
        ]
    
    return filtered

def main():
    st.title("📊 Radar de Vagas de Dados em Startups")
    
    st.markdown("""
    Busca vagas relacionadas à **área de dados** em startups que utilizam o ATS **InHire**.
    """)
    
    companies = load_companies()
    
    if not companies:
        st.error("Nenhuma empresa foi carregada.")
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info(f"📋 Empresas a processar: **{len(companies)}**")
    
    with col2:
        if st.button("🔍 Buscar Vagas", key="search_button", use_container_width=True):
            st.session_state.search_triggered = True
    
    if 'search_triggered' not in st.session_state:
        st.session_state.search_triggered = False
    
    if st.session_state.search_triggered:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_jobs = []
        companies_processed = 0
        
        for company in companies:
            status_text.text(f"🔄 Buscando em: {company}")
            
            jobs = scrape_jobs(company)
            data_jobs = [job for job in jobs if is_data_job(job['titulo'])]
            all_jobs.extend(data_jobs)
            
            companies_processed += 1
            progress_bar.progress(companies_processed / len(companies))
            
            time.sleep(0.5)
        
        status_text.text("✅ Busca concluída!")
        progress_bar.empty()
        
        if all_jobs:
            df = pd.DataFrame(all_jobs)
            df = df[['empresa', 'titulo', 'localidade', 'link']]
            st.session_state.df_jobs = df
            st.session_state.jobs_count = len(df)
        else:
            st.session_state.df_jobs = pd.DataFrame()
            st.session_state.jobs_count = 0
    
    if 'df_jobs' in st.session_state and len(st.session_state.df_jobs) > 0:
        df = st.session_state.df_jobs
        
        st.success(f"✨ **{st.session_state.jobs_count} vagas encontradas!**")
        
        st.markdown("---")
        st.subheader("🔎 Filtros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            companies_list = ["Todas"] + sorted(df['empresa'].unique().tolist())
            filter_company = st.selectbox("Filtrar por Empresa:", companies_list, key="filter_company")
        
        with col2:
            filter_keyword = st.text_input("Filtrar por Palavra:", placeholder="Ex: Engineer, Analyst...", key="filter_keyword")
        
        df_filtered = filter_jobs(df, filter_company, filter_keyword)
        
        st.markdown("---")
        st.subheader(f"📌 Vagas ({len(df_filtered)} resultados)")
        
        display_df = df_filtered.copy()
        display_df.columns = ['Empresa', 'Vaga', 'Local', 'Link']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        export_df = df_filtered.copy()
        export_df.columns = ['Empresa', 'Vaga', 'Local', 'Link']
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            export_df.to_excel(writer, sheet_name='Vagas', index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 Baixar em Excel",
            data=output.getvalue(),
            file_name="vagas_dados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("📈 Estatísticas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", len(df_filtered))
        with col2:
            st.metric("Empresas", df_filtered['empresa'].nunique())
        with col3:
            remote = df_filtered[df_filtered['localidade'].apply(is_remote_job)].shape[0]
            st.metric("Remotas", remote)
        with col4:
            presencial = df_filtered[~df_filtered['localidade'].apply(is_remote_job)].shape[0]
            st.metric("Presenciais", presencial)
    
    elif st.session_state.search_triggered:
        st.warning("⚠️ Nenhuma vaga encontrada.")

if __name__ == "__main__":
    main()
