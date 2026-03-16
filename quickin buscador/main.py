import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import unicodedata
import re
from datetime import datetime

st.set_page_config(page_title="Scanner de Vagas Pro", layout="wide")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def limpar_texto(texto):
    if not texto: return ""
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r'[^a-zA-Z0-9\s]', '', texto).lower().strip()

def extrair_vagas_quickin(slug_empresa):
    vagas_da_empresa = []
    for pagina in range(1, 10): # Varre as 3 primeiras páginas
        url = f"https://jobs.quickin.io/{slug_empresa}/jobs?page={pagina}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200: break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            linhas = soup.find_all('tr')
            vagas_na_pagina = 0
            
            for linha in linhas:
                link_tag = linha.find('a', href=True)
                if link_tag and f"/{slug_empresa}/jobs/" in link_tag['href']:
                    titulo = link_tag.get_text(strip=True)
                    href = link_tag['href']
                    full_link = f"https://jobs.quickin.io{href}" if href.startswith('/') else href
                    
                    # Captura Modalidade
                    badge = linha.find('span', class_='badge')
                    modalidade_raw = badge.get_text(strip=True).lower() if badge else "presencial"
                    
                    if "remote" in modalidade_raw: modalidade = "Remoto"
                    elif "hybrid" in modalidade_raw or "hibrido" in modalidade_raw: modalidade = "Híbrido"
                    else: modalidade = "Presencial"

                    # Data de Criação: O Quickin muitas vezes não mostra a data na linha da tabela,
                    # mas se houver algum campo de data ou texto relativo, tentamos pegar.
                    # Caso contrário, marcamos como "Recente" (já que o site ordena por novas)
                    data_vaga = "Recente" 
                    
                    vagas_da_empresa.append({
                        "Empresa": slug_empresa.upper(),
                        "Data": data_vaga,
                        "Vaga": titulo,
                        "Modalidade": modalidade,
                        "Link": full_link
                    })
                    vagas_na_pagina += 1
            
            if vagas_na_pagina == 0: break
            time.sleep(0.3)
        except:
            break
            
    return vagas_da_empresa

st.title("🎯 Scanner de Oportunidades Quickin")

with st.sidebar:
    st.header("Filtros")
    termos_input = st.text_input("Termos de busca", value="Dados, Negocios")
    modalidades_alvo = st.multiselect(
        "Modalidades:",
        ["Remoto", "Híbrido", "Presencial"],
        default=["Remoto", "Híbrido"]
    )

if st.button("🚀 Iniciar Busca"):

############# Adicione aqui as empresas a serem buscadas #####################
    empresas = [
    # Empresas diretas (clientes do Quickin)
    "domvsit",
    "sinqia",           # Agora opera como Evertec Brasil
    "startse",
    "nexer",
    "winnin",
    "ip4y",
    "base2",
    "qintess",
    "ipm",
    "nposistemas",
    "computecnica",
    "uex",
    "indt",
    "infox",
    "reply",
    "geoambiente",
    "reponto",
    "tecadi",
    "macfor",
    "alifenino",
    "registradores",    # ONR

    # Consultorias / RH que postam vagas para clientes
    "leansales",
    "humtech",
    "recrutame",
    "recrutify",
    "connectforpeople",
    "peopleconsulting",
    "peopletalent",
    "arttha",
    "newjob",
    "vagas",            # Time de Recrutamento (genérico)
    "vagasconsultoria",
    "gruponunchi",
    "captativa",
    "holiste",
    "saferes",
    "techrx",
    "rhgrandestalentos",
    "pessoalizerh",
    "talentsclub",
    "npwdigital",
    "jobi-hub",
]

    termos_busca = [limpar_texto(t) for t in termos_input.split(",")]
    
    resultados = []
    status = st.empty()
    
    for emp in empresas:
        status.info(f"Escaneando {emp}...")
        vagas_brutas = extrair_vagas_quickin(emp)
        
        for v in vagas_brutas:
            titulo_limpo = limpar_texto(v['Vaga'])
            match_termo = any(termo in titulo_limpo for termo in termos_busca)
            match_mod = v['Modalidade'] in modalidades_alvo
            
            if match_termo and match_mod:
                resultados.append(v)

    status.empty()

    if resultados:
        st.success(f"Encontramos {len(resultados)} matches!")
        
        # Criando a visualização com botões
        for res in resultados:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
                with col1:
                    st.write(f"**{res['Empresa']}**")
                with col2:
                    st.write(res['Vaga'])
                with col3:
                    st.write(f"📍 {res['Modalidade']}")
                with col4:
                    # O segredo do botão: Link estilizado como botão
                    st.link_button("Abrir Vaga", res['Link'], use_container_width=True)
                st.divider()
    else:
        st.warning("Nenhuma vaga encontrada para os filtros aplicados.")