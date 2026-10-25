"""Streamlit frontend — Supply Chain AI."""
import os
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Supply Chain AI", page_icon="🏭", layout="wide")

DB_PATH = Path(__file__).parent.parent / "data" / "supply_chain.duckdb"


@st.cache_data
def load_kpis() -> dict:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    row = con.execute("""
        SELECT
          (SELECT COUNT(*) FROM suppliers) AS n_suppliers,
          (SELECT COUNT(*) FROM products) AS n_products,
          (SELECT COUNT(*) FROM orders) AS n_orders,
          (SELECT ROUND(SUM(quantity * unit_price), 2) FROM orders) AS gmv,
          (SELECT ROUND(AVG(rating), 2) FROM suppliers) AS avg_supplier_rating
    """).fetchone()
    con.close()
    return dict(zip(["n_suppliers", "n_products", "n_orders", "gmv", "avg_supplier_rating"], row))


@st.cache_data
def load_supplier_perf() -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("SELECT * FROM marts.mart_supplier_performance ORDER BY gmv DESC").df()
    con.close()
    return df


@st.cache_data
def load_orders_ts() -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT order_date::DATE AS day, COUNT(*) AS n_orders, SUM(quantity * unit_price) AS gmv
        FROM orders GROUP BY 1 ORDER BY 1
    """).df()
    con.close()
    return df


st.title("🏭 Supply Chain AI")
st.caption("Plataforma de analytics + IA para supply chain · FastAPI · dbt · DuckDB · LLM")

if not DB_PATH.exists():
    st.error(f"Banco nao encontrado em {DB_PATH}. Rode: python -m api.seed")
    st.stop()

# KPIs
kpis = load_kpis()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Suppliers", f"{kpis['n_suppliers']:,}")
c2.metric("Products", f"{kpis['n_products']:,}")
c3.metric("Orders", f"{kpis['n_orders']:,}")
c4.metric("GMV", f"R$ {kpis['gmv']/1e6:.1f}M")
c5.metric("Avg rating", f"{kpis['avg_supplier_rating']:.2f}")

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Visao geral", "🏆 Suppliers", "🤖 Pergunte à IA", "🛠️ Debug"])

with tab1:
    st.subheader("Pedidos por dia")
    df = load_orders_ts()
    st.line_chart(df.set_index("day")[["n_orders"]])
    st.subheader("GMV por dia")
    st.line_chart(df.set_index("day")[["gmv"]])

with tab2:
    st.subheader("Performance por supplier")
    perf = load_supplier_perf()
    st.dataframe(perf, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Pergunte em linguagem natural")
    st.caption("O LLM gera SQL, executa no DuckDB, e sintetiza a resposta (RAG)")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.warning("⚠️ `GROQ_API_KEY` nao configurada. Crie gratis em https://console.groq.com/keys")
        st.code("echo GROQ_API_KEY=sua_chave >> .env", language="bash")
    else:
        question = st.text_input("Ex: Qual supplier tem mais pedidos atrasados?")
        if st.button("Perguntar") and question:
            with st.spinner("Gerando SQL + consultando + sintetizando..."):
                try:
                    from rag.llm import answer_question
                    answer, sources, model = answer_question(question, api_key)
                    st.success(answer)
                    with st.expander("Fontes (SQL gerado)"):
                        for s in sources:
                            st.code(s, language="sql")
                    st.caption(f"Modelo: {model}")
                except Exception as e:
                    st.error(f"Erro: {e}")

with tab4:
    st.subheader("Debug SQL")
    st.caption("Consultas read-only para explorar")
    sql = st.text_area("SQL", "SELECT * FROM orders LIMIT 10", height=150)
    if st.button("Executar"):
        try:
            con = duckdb.connect(str(DB_PATH), read_only=True)
            df = con.execute(sql).df()
            con.close()
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Erro: {e}")