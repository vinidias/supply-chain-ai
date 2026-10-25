"""RAG over supply chain data — Groq (Llama 3.3) + LangChain."""
from __future__ import annotations

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from api import db

MODEL = "llama-3.3-70b-versatile"

# Schema textual (contexto para o LLM gerar SQL)
SCHEMA = """
Tabelas disponiveis (DuckDB, SQL padrao):

suppliers(id INT, name TEXT, country TEXT, category TEXT, rating REAL)
products(id INT, name TEXT, category TEXT, supplier_id INT, unit_cost REAL, lead_time_days INT)
orders(id INT, product_id INT, order_date TIMESTAMP, quantity INT, unit_price REAL, status TEXT)
inventory(product_id INT, snapshot_date TIMESTAMP, stock_level INT, reorder_point INT)

status possiveis em orders: delivered, in_transit, delayed, cancelled
""".strip()


def _generate_sql(question: str, api_key: str) -> str:
    """Pede ao LLM para gerar uma query SQL a partir da pergunta."""
    llm = ChatGroq(api_key=api_key, model=MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Voce e um analista de dados senior. Gere APENAS SQL valido (DuckDB) para responder a pergunta. Sem markdown, sem explicacao. Use apenas as tabelas do schema."),
        ("human", f"Schema:\n{SCHEMA}\n\nPergunta: {{question}}\n\nSQL:"),
    ])
    chain = prompt | llm | StrOutputParser()
    sql = chain.invoke({"question": question}).strip()
    # limpar possiveis fences
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[-1]
        if sql.endswith("```"):
            sql = sql.rsplit("```", 1)[0]
    return sql.strip().rstrip(";")


def _execute_sql(sql: str) -> list[dict]:
    """Executa SQL com protecao contra DML malicioso."""
    forbidden = ("INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE", "GRANT", "REVOKE")
    sql_upper = sql.upper()
    for token in forbidden:
        if token in sql_upper:
            raise ValueError(f"Query bloqueada: contem {token}")
    return db.query(sql)


def _summarize(question: str, sql: str, results: list[dict], api_key: str) -> str:
    """Pede ao LLM para transformar os resultados em resposta natural."""
    llm = ChatGroq(api_key=api_key, model=MODEL, temperature=0.3)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Voce e um analista de supply chain. Responda de forma clara, direta e em portugues. Use os numeros do resultado. Se vazio, diga que nao encontrou dados."),
        ("human", "Pergunta: {question}\n\nSQL executado:\n{sql}\n\nResultado (primeiras 20 linhas):\n{results}\n\nResposta:"),
    ])
    chain = prompt | llm | StrOutputParser()
    preview = results[:20]
    return chain.invoke({"question": question, "sql": sql, "results": str(preview)})


def answer_question(question: str, api_key: str) -> tuple[str, list[str], str]:
    """RAG: gera SQL, executa, sintetiza resposta. Retorna (answer, sources, model)."""
    sql = _generate_sql(question, api_key)
    results = _execute_sql(sql)
    answer = _summarize(question, sql, results, api_key)
    return answer, [f"SQL: {sql}"], MODEL