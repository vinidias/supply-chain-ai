"""
AI Agent com tool calling (LangChain + Groq).

O agent pode:
    1. Consultar KPIs (metrics/summary)
    2. Listar produtos em falta (inventory/low-stock)
    3. Pedidos recentes por status
    4. Executar SQL read-only custom
"""
from __future__ import annotations

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from api import db

MODEL = "llama-3.3-70b-versatile"


@tool
def get_kpis() -> str:
    """Retorna KPIs gerais: # suppliers, # products, # orders, GMV, rating medio, # atrasados."""
    rows = db.query("""
        SELECT
          (SELECT COUNT(*) FROM suppliers) AS n_suppliers,
          (SELECT COUNT(*) FROM products) AS n_products,
          (SELECT COUNT(*) FROM orders) AS n_orders,
          (SELECT ROUND(SUM(quantity * unit_price), 2) FROM orders) AS gmv,
          (SELECT ROUND(AVG(rating), 2) FROM suppliers) AS avg_supplier_rating,
          (SELECT COUNT(*) FROM orders WHERE status = 'delayed') AS n_delayed_orders
    """)
    return str(rows[0])


@tool
def get_low_stock(limit: int = 10) -> str:
    """Retorna os produtos com estoque abaixo do reorder point. Parametro: limit (default 10)."""
    rows = db.query("""
        WITH latest AS (
            SELECT product_id, stock_level, reorder_point,
                   ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY snapshot_date DESC) AS rn
            FROM inventory
        )
        SELECT l.product_id, p.name AS product_name, l.stock_level, l.reorder_point
        FROM latest l
        LEFT JOIN products p ON p.id = l.product_id
        WHERE l.rn = 1 AND l.stock_level < l.reorder_point
        ORDER BY (l.stock_level - l.reorder_point) ASC
        LIMIT :limit
    """, {"limit": limit})
    return str(rows)


@tool
def get_delayed_orders(limit: int = 10) -> str:
    """Retorna os pedidos com status delayed. Parametro: limit (default 10)."""
    rows = db.query("""
        SELECT o.id, o.product_id, p.name AS product_name, o.quantity, o.order_date
        FROM orders o
        LEFT JOIN products p ON p.id = o.product_id
        WHERE o.status = 'delayed'
        ORDER BY o.order_date DESC
        LIMIT :limit
    """, {"limit": limit})
    return str(rows)


@tool
def run_sql(query: str) -> str:
    """Executa uma query SQL read-only no DuckDB e retorna o resultado. Use apenas SELECT."""
    q_upper = query.upper()
    for forbidden in ("INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER"):
        if forbidden in q_upper:
            return f"BLOQUEADO: query contem {forbidden}. Apenas SELECT e permitido."
    try:
        rows = db.query(query)
        return str(rows[:50])
    except Exception as e:
        return f"ERRO: {e}"


SYSTEM_PROMPT = """Voce e um assistente de supply chain inteligente.
Responda em portugues. Use as ferramentas disponiveis para consultar dados reais antes de responder.
Nunca invente numeros. Cite quais ferramentas usou. Se nao souber, diga "nao tenho essa informacao".
"""


def build_agent(api_key: str) -> AgentExecutor:
    llm = ChatGroq(api_key=api_key, model=MODEL, temperature=0)
    tools = [get_kpis, get_low_stock, get_delayed_orders, run_sql]
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=5)


def ask_agent(question: str, api_key: str) -> str:
    executor = build_agent(api_key)
    result = executor.invoke({"input": question})
    return result.get("output", "Sem resposta")
