"""
🔍 Monitor de Vagas InHire
App Streamlit para buscar vagas remotas de Analista de Dados

Autor: Desenvolvedor Python Sênior
Data: Março 2026
"""

import streamlit as st
from googlesearch import search
import pandas as pd
import re
from datetime import datetime
import time

# ==================== CONFIGURAÇÕES ====================

st.set_page_config(
    page_title="Monitor Vagas InHire",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== TODAS AS EMPRESAS ====================

TODAS_EMPRESAS = [
    "sympla", "agenciacriativa", "agrosearch", "alice", "alun", "amcom", 
    "auvotecnologia", "bankme", "betaonline", "brasilparalelo", "ceisc", 
    "cerc", "cielo", "cora", "crown", "db1", "deloitte", "digix", 
    "fitenergia", "flash", "flutterbrazil", "fretadao", "gex", "grupoescalar", 
    "gx2", "infotecbrasil", "kanastra", "kpmg", "livemode", "magalu", 
    "magazord", "milvus", "mjv", "nomadglobal", "olist", "openlabs", 
    "orizon", "paytrack", "pier", "premiersoft", "qive", "radix", 
    "residclub", "sanar", "sharepeoplehub", "shareprime", "supertex", 
    "sylvamo", "talentt", "talentx", "tripla", "unimar", "upflux", 
    "v360", "v4company", "vitru", "warren", "zig", "contabilizei", 
    "kiwify", "loft", "nubank", "creditas", "ifood", "stone", "loggi"
]

# ==================== FUNÇÕES ====================

def buscar_vagas_google(query, num_results=20):
    """Busca vagas usando Google Search."""
    resultados = []
    
    try:
        results = search(query, num_results=num_results, lang='pt', advanced=True)
        
        for result in results:
            url = result.url
            title = result.title or ""
            description = result.description or ""
            
            if 'inhire.app/vagas' in url:
                match = re.search(r'https?://([a-zA-Z0-9-]+)\.inhire\.app', url)
                empresa = match.group(1).upper() if match else "DESCONHECIDA"
                
                resultados.append({
                    'empresa': empresa,
                    'titulo': title,
                    'descricao': description,
                    'link': url,
                })
        
    except Exception as e:
        st.error(f"Erro na busca: {str(e)}")
    
    return resultados


def filtrar_vagas(vagas, keywords_cargos, keywords_remoto):
    """Remove duplicatas e filtra por relevância."""
    vagas_filtradas = []
    urls_vistas = set()
    
    for vaga in vagas:
        url = vaga['link']
        
        if url in urls_vistas:
            continue
        urls_vistas.add(url)
        
        texto = (vaga['titulo'] + ' ' + vaga['descricao']).lower()
        
        tem_cargo = any(cargo.lower() in texto for cargo in keywords_cargos)
        tem_remoto = any(remoto.lower() in texto for remoto in keywords_remoto)
        
        if (tem_cargo and tem_remoto) or tem_cargo:
            vagas_filtradas.append(vaga)
    
    return vagas_filtradas


# ==================== INTERFACE ====================

st.title("🔍 Monitor de Vagas InHire")
st.markdown("### Encontre vagas remotas de Analista de Dados automaticamente")

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações")

# Seleção de empresas
st.sidebar.subheader("🏢 Empresas")

empresas_top = ["sympla", "kpmg", "ifood", "nubank", "stone", "creditas", "magalu"]
empresas_selecionadas = st.sidebar.multiselect(
    "Selecione empresas prioritárias:",
    options=TODAS_EMPRESAS,
    default=empresas_top,
    help="Empresas selecionadas terão buscas individuais"
)

buscar_todas = st.sidebar.checkbox(
    "Incluir busca geral (todas empresas)",
    value=True,
    help="Faz uma busca em todas as empresas de uma vez"
)

# Keywords de cargos
st.sidebar.subheader("💼 Cargos")
keywords_cargos_default = [
    "analista de dados",
    "data analyst",
    "business analyst",
    "data engineer",
    "data scientist"
]

keywords_cargos_input = st.sidebar.text_area(
    "Keywords de cargos (uma por linha):",
    value="\n".join(keywords_cargos_default),
    height=150
)
keywords_cargos = [k.strip() for k in keywords_cargos_input.split('\n') if k.strip()]

# Keywords de remoto
st.sidebar.subheader("🏠 Modalidade")
keywords_remoto_default = ["remoto", "remote", "home office"]

keywords_remoto_input = st.sidebar.text_area(
    "Keywords de remoto (uma por linha):",
    value="\n".join(keywords_remoto_default),
    height=80
)
keywords_remoto = [k.strip() for k in keywords_remoto_input.split('\n') if k.strip()]

# Configurações avançadas
st.sidebar.subheader("🔧 Avançado")
num_resultados_geral = st.sidebar.slider(
    "Resultados da busca geral:",
    min_value=10,
    max_value=100,
    value=50,
    step=10
)

num_resultados_empresa = st.sidebar.slider(
    "Resultados por empresa:",
    min_value=5,
    max_value=30,
    value=10,
    step=5
)

delay = st.sidebar.slider(
    "Delay entre buscas (segundos):",
    min_value=1,
    max_value=10,
    value=2,
    step=1,
    help="Aumente se estiver sendo bloqueado"
)

# ==================== BOTÃO DE BUSCA ====================

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    botao_buscar = st.button(
        "🚀 BUSCAR VAGAS",
        type="primary",
        use_container_width=True
    )

st.markdown("---")

# ==================== EXECUÇÃO ====================

if botao_buscar:
    st.info("🔍 Iniciando busca de vagas...")
    
    # Constrói queries
    queries = []
    
    # Query geral
    if buscar_todas:
        cargos_or = ' OR '.join([f'"{cargo}"' for cargo in keywords_cargos])
        remoto_or = ' OR '.join([f'"{r}"' for r in keywords_remoto])
        query_geral = f'site:inhire.app/vagas ({cargos_or}) ({remoto_or})'
        queries.append(("GERAL - Todas Empresas", query_geral, num_resultados_geral))
    
    # Queries por empresa
    for empresa in empresas_selecionadas:
        cargos_or = ' OR '.join([f'"{cargo}"' for cargo in keywords_cargos])
        query_empresa = f'site:{empresa}.inhire.app/vagas ({cargos_or})'
        queries.append((empresa.upper(), query_empresa, num_resultados_empresa))
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Executa buscas
    todas_vagas = []
    
    for i, (nome, query, num_results) in enumerate(queries):
        status_text.text(f"[{i+1}/{len(queries)}] Buscando: {nome}...")
        progress_bar.progress((i + 1) / len(queries))
        
        vagas = buscar_vagas_google(query, num_results)
        todas_vagas.extend(vagas)
        
        if i < len(queries) - 1:
            time.sleep(delay)
    
    status_text.empty()
    progress_bar.empty()
    
    # Filtra resultados
    st.info(f"📊 Processando {len(todas_vagas)} resultados brutos...")
    vagas_filtradas = filtrar_vagas(todas_vagas, keywords_cargos, keywords_remoto)
    
    # Resultados
    if vagas_filtradas:
        st.success(f"✅ {len(vagas_filtradas)} vagas relevantes encontradas!")
        
        # Cria DataFrame
        df = pd.DataFrame(vagas_filtradas)
        df = df[['empresa', 'titulo', 'descricao', 'link']]
        df.columns = ['Empresa', 'Título', 'Descrição', 'Link']
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Vagas", len(df))
        
        with col2:
            st.metric("Empresas", df['Empresa'].nunique())
        
        with col3:
            vagas_hoje = len(df)  # Placeholder
            st.metric("Processadas", vagas_hoje)
        
        # Gráfico de empresas
        st.subheader("📊 Distribuição por Empresa")
        empresas_count = df['Empresa'].value_counts().head(10)
        st.bar_chart(empresas_count)
        
        # Tabela de resultados
        st.subheader("📋 Vagas Encontradas")
        
        # Filtro interativo
        empresas_filtro = st.multiselect(
            "Filtrar por empresa:",
            options=sorted(df['Empresa'].unique()),
            default=None
        )
        
        if empresas_filtro:
            df_display = df[df['Empresa'].isin(empresas_filtro)]
        else:
            df_display = df
        
        # Exibe tabela
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Link": st.column_config.LinkColumn("Link Direto")
            }
        )
        
        # Download
        st.subheader("💾 Download")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"vagas_inhire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel usando buffer
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Vagas')
            excel_data = output.getvalue()
            
            st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name=f"vagas_inhire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    
    else:
        st.warning("⚠️ Nenhuma vaga encontrada com os critérios selecionados.")
        st.info("""
        **Sugestões:**
        - Aumente o número de resultados
        - Reduza os filtros
        - Tente outras empresas
        - Execute novamente em alguns minutos
        """)

# ==================== RODAPÉ ====================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🔍 Monitor de Vagas InHire v1.0</p>
    <p>Desenvolvido para encontrar vagas remotas de Analista de Dados</p>
    <p>⚡ Executando na nuvem via Streamlit Cloud</p>
</div>
""", unsafe_allow_html=True)
