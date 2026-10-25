"""
LLM + RAG multi-provider (Groq, Ark/Volcengine, OpenAI).

Providers suportados (via env var LLM_PROVIDER):
    groq     : GROQ_API_KEY (gratis, Llama 3.3 70B)
    ark      : ARK_API_KEY  (Volcengine Ark / Doubao)
    openai   : OPENAI_API_KEY (GPT-4o-mini)
"""
from __future__ import annotations

import os
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from api import db

SCHEMA = """
Tabelas disponiveis (DuckDB, SQL padrao compativel com BigQuery):

suppliers(id INT, name TEXT, country TEXT, category TEXT, rating REAL)
products(id INT, name TEXT, category TEXT, supplier_id INT, unit_cost REAL, lead_time_days INT)
orders(id INT, product_id INT, order_date TIMESTAMP, quantity INT, unit_price REAL, status TEXT)
inventory(product_id INT, snapshot_date TIMESTAMP, stock_level INT, reorder_point INT)

status possiveis: delivered, in_transit, delayed, cancelled
""".strip()


def _build_llm(temperature: float = 0.0) -> tuple[BaseChatModel, str]:
    """Retorna (llm, provider_name) baseado em env vars."""
    provider = os.getenv("LLM_PROVIDER", "").lower()

    # Auto-detect se LLM_PROVIDER nao setado
    if not provider:
        if os.getenv("GROQ_API_KEY"):
            provider = "groq"
        elif os.getenv("ARK_API_KEY"):
            provider = "ark"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            raise ValueError("Nenhum provider configurado. Sete GROQ_API_KEY, ARK_API_KEY ou OPENAI_API_KEY.")

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=os.environ["GROQ_API_KEY"],
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            temperature=temperature,
        ), "groq"

    if provider == "ark":
        # Volcengine Ark usa API compativel com OpenAI
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=os.environ["ARK_API_KEY"],
            base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            model=os.getenv("ARK_MODEL", "doubao-pro-32k"),
            temperature=temperature,
        ), "ark"

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
        ), "openai"

    raise ValueError(f"Provider desconhecido: {provider}")


def _generate_sql(question: str, llm: BaseChatModel) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Voce e um analista de dados senior. Gere APENAS SQL valido (DuckDB, compativel com BigQuery) para responder a pergunta. Sem markdown, sem explicacao. Use apenas as tabelas do schema."),
        ("human", f"Schema:\n{SCHEMA}\n\nPergunta: {{question}}\n\nSQL:"),
    ])
    chain = prompt | llm | StrOutputParser()
    sql = chain.invoke({"question": question}).strip()
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[-1]
        if sql.endswith("```"):
            sql = sql.rsplit("```", 1)[0]
    return sql.strip().rstrip(";")


def _execute_sql(sql: str) -> list[dict]:
    forbidden = ("INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE", "GRANT", "REVOKE")
    sql_upper = sql.upper()
    for token in forbidden:
        if token in sql_upper:
            raise ValueError(f"Query bloqueada: contem {token}")
    return db.query(sql)


def _summarize(question: str, sql: str, results: list[dict], llm: BaseChatModel) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Voce e um analista de supply chain. Responda de forma clara, direta e em portugues. Use os numeros do resultado. Se vazio, diga que nao encontrou dados."),
        ("human", "Pergunta: {question}\n\nSQL executado:\n{sql}\n\nResultado (primeiras 20 linhas):\n{results}\n\nResposta:"),
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"question": question, "sql": sql, "results": str(results[:20])})


def answer_question(question: str) -> tuple[str, list[str], str]:
    llm, provider = _build_llm(temperature=0.0)
    sql = _generate_sql(question, llm)
    results = _execute_sql(sql)
    answer = _summarize(question, sql, results, llm)
    return answer, [f"SQL: {sql}"], provider
