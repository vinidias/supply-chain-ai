{{ config(materialized="table", schema="marts") }}

-- Performance por supplier: GMV, # pedidos, taxa de atraso
WITH orders_by_supplier AS (
    SELECT
        p.supplier_id,
        COUNT(o.order_id) AS n_orders,
        SUM(o.line_total) AS gmv,
        SUM(CASE WHEN o.status = 'delayed' THEN 1 ELSE 0 END) AS n_delayed,
        ROUND(100.0 * SUM(CASE WHEN o.status = 'delayed' THEN 1 ELSE 0 END) / COUNT(o.order_id), 2) AS delay_pct
    FROM {{ ref('stg_orders') }} o
    LEFT JOIN products p ON p.id = o.product_id
    GROUP BY p.supplier_id
)
SELECT
    s.supplier_id,
    s.supplier_name,
    s.country,
    s.category,
    s.rating,
    COALESCE(o.n_orders, 0) AS n_orders,
    COALESCE(o.gmv, 0) AS gmv,
    COALESCE(o.n_delayed, 0) AS n_delayed,
    COALESCE(o.delay_pct, 0) AS delay_pct
FROM {{ ref('stg_suppliers') }} s
LEFT JOIN orders_by_supplier o ON o.supplier_id = s.supplier_id