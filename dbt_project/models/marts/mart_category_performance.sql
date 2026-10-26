{{ config(materialized="table", schema="marts") }}

-- Performance agregada por categoria de produto
-- Combina stg_products + stg_orders (dbt resolve a ordem sozinho)

WITH products_per_cat AS (
    SELECT
        category,
        COUNT(DISTINCT product_id) AS n_products,
        AVG(unit_cost) AS avg_unit_cost
    FROM {{ ref('stg_products') }}
    GROUP BY category
),

orders_per_cat AS (
    SELECT
        p.category,
        COUNT(o.order_id) AS n_orders,
        SUM(o.line_total) AS gmv,
        AVG(o.line_total) AS avg_ticket,
        SUM(CASE WHEN o.status = 'delayed' THEN 1 ELSE 0 END) AS n_delayed
    FROM {{ ref('stg_orders') }} o
    LEFT JOIN {{ ref('stg_products') }} p ON p.product_id = o.product_id
    GROUP BY p.category
)

SELECT
    COALESCE(ppc.category, opc.category) AS category,
    COALESCE(ppc.n_products, 0) AS n_products,
    COALESCE(opc.n_orders, 0) AS n_orders,
    COALESCE(ROUND(opc.gmv, 2), 0) AS gmv,
    COALESCE(ROUND(opc.avg_ticket, 2), 0) AS avg_ticket,
    COALESCE(opc.n_delayed, 0) AS n_delayed,
    COALESCE(ROUND(100.0 * opc.n_delayed / NULLIF(opc.n_orders, 0), 2), 0) AS delay_rate_pct,
    COALESCE(ROUND(ppc.avg_unit_cost, 2), 0) AS avg_unit_cost
FROM products_per_cat ppc
FULL OUTER JOIN orders_per_cat opc ON opc.category = ppc.category
ORDER BY gmv DESC
