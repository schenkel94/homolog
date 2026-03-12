import streamlit as st
import pandas as pd

st.set_page_config(page_title="Radar de Vagas de Dados", layout="wide")

st.title("📊 Radar de Vagas de Dados")

try:
    df = pd.read_csv("jobs.csv")
except:
    st.error("Arquivo jobs.csv não encontrado")
    st.stop()

if df.empty:
    st.warning("Nenhuma vaga encontrada ainda.")
    st.stop()

# converter data
df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

col1, col2 = st.columns(2)

col1.metric("Total de vagas", len(df))
col2.metric("Empresas", df["empresa"].nunique())

st.divider()

empresa = st.multiselect(
    "Filtrar empresa",
    df["empresa"].unique()
)

if empresa:
    df = df[df["empresa"].isin(empresa)]

st.dataframe(
    df.sort_values("updated_at", ascending=False),
    use_container_width=True
)