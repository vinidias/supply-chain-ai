# Post LinkedIn — Supply Chain AI

**Caracteres:** ~1.800 (dentro do limite do LinkedIn)

---

**Construí uma plataforma de supply chain com IA do zero em 2 dias** 🏭

Não é um protótipo. É produção:
✅ 8 endpoints REST (FastAPI)
✅ 6 modelos dbt com testes automáticos
✅ RAG multi-provider (Groq + BytePlus Ark)
✅ AI agent com tool calling (4 tools)
✅ Dashboard em SQL puro (anofox-visualization)
✅ CI verde (lint + 8 testes pytest + dbt test)
✅ Docker + compose pronta para deploy

**A parte mais interessante: o dashboard é 100% SQL.**

Sem JavaScript. Sem biblioteca de chart. O SQL É o dashboard:

```sql
SELECT anofox_bar(supplier_name, gmv)
FROM marts.mart_supplier_performance
ORDER BY gmv DESC
LIMIT 10
```

→ vira o bar chart que você vê abaixo. Em SVG. Renderizado pelo DuckDB.

**O RAG também funciona nos 2 providers (respostas idênticas):**

Pergunta: "Qual o supplier com maior GMV?"
→ Supplier_012 · R$ 20.883.441,46 (SQL gerado + resposta)

Pergunta: "Quantos pedidos foram atrasados?"
→ 312

Pergunta: "Qual o ticket médio?"
→ R$ 82.352,05

**Stack completa:**
• FastAPI + SQLAlchemy + DuckDB (portable → PostgreSQL em 1 linha)
• dbt-core (staging → marts + 6 tests)
• LangChain + Groq (gpt-oss-120b) + BytePlus Ark (seed-2-0-lite)
• Anofox-visualization (charts from SQL)
• Streamlit (4 tabs)
• Docker + docker-compose
• GitHub Actions CI

**12 de 12 requisitos da vaga cobertos.** 100% open source.

📦 github.com/vinidias/supply-chain-ai

#DataEngineering #AI #RAG #dbt #FastAPI #SupplyChain #Python #MachineLearning #LLM
