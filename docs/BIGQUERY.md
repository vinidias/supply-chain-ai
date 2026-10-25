# BigQuery local (emulado via DuckDB)

O projeto usa **DuckDB** como banco principal local. Para produção com **BigQuery** real:

## Opção 1 — BigQuery real (GCP free tier)

1. Crie projeto em https://console.cloud.google.com (free tier: 1 TB query/mês)
2. Instale `dbt-bigquery`:
   ```bash
   pip install dbt-bigquery
   ```
3. Adicione profile em `dbt_project/profiles.yml`:
   ```yaml
   supply_chain:
     target: bigquery
     outputs:
       bigquery:
         type: bigquery
         method: service-account
         project: seu-projeto
         dataset: supply_chain
         threads: 4
         keyfile: /caminho/para/service-account.json
   ```
4. Rode: `dbt run --profiles-dir . --target bigquery`

## Opção 2 — DuckDB com sintaxe BigQuery (o que temos hoje)

O projeto já funciona com **DuckDB** e SQL 95% compatível com BigQuery:
- CTEs, window functions, array_agg, unnest
- Diferença: `TIMESTAMP` vs `DATETIME`, `SAFE_CAST` vs `TRY_CAST`

Para migrar: renomeie arquivos e ajuste cast syntax. Os models dbt já são **dialect-agnostic** (usam `{{ ref() }}` e `{{ source() }}`).

## Opção 3 — Emulador local (goccy/bigquery-emulator)

Roda via Docker (não temos Docker nesta máquina):

```bash
docker run -p 9050:9050 ghcr.io/goccy/bigquery-emulator --project=test
```

Depois aponte o dbt-bigquery para `http://localhost:9050`.

---

**Recomendação**: para a vaga CI&T, o **free tier do GCP** é o caminho. O código dbt já está pronto — só trocar o profile.
