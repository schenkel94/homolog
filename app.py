import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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

@st.cache_resource
def get_driver():
    """Cria driver Selenium com cache"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    return driver

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

def scrape_jobs_with_selenium(company_name):
    """Scrape com Selenium para renderizar JavaScript"""
    url = f"https://{company_name}.inhire.app/vagas"
    
    try:
        driver = get_driver()
        driver.get(url)
        
        # Aguarda o carregamento dos elementos
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "css-uormui"))
            )
        except:
            pass
        
        time.sleep(2)  # Aguarda renderização completa
        
        # Pega o HTML renderizado
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        # Encontra todos os itens de vaga
        job_items = soup.find_all('li', class_='css-1klv894')
        
        for item in job_items:
            try:
                # Encontra o link
                link_elem = item.find('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                link = link_elem.get('href', '')
                
                # Encontra o título
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
        
        return jobs
        
    except Exception as e:
        st.error(f"Erro ao processar {company_name}: {str(e)}")
        return []
    finally:
        try:
            driver.quit()
        except:
            pass

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
            
            jobs = scrape_jobs_with_selenium(company)
            data_jobs = [job for job in jobs if is_data_job(job['titulo'])]
            all_jobs.extend(data_jobs)
            
            companies_processed += 1
            progress_bar.progress(companies_processed / len(companies))
        
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
