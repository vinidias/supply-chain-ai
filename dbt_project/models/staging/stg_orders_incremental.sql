{{ config(
    materialized='incremental',
    unique_key='order_id',
    schema='staging'
) }}

-- Versão incremental de stg_orders: só processa pedidos novos a partir
-- da última execução (padrão de produção em tabelas grandes)

SELECT
    o.id AS order_id,
    o.product_id,
    p.name AS product_name,
    p.category,
    o.order_date,
    o.quantity,
    o.unit_price,
    ROUND(o.quantity * o.unit_price, 2) AS line_total,
    o.status
FROM orders o
LEFT JOIN products p ON p.id = o.product_id

{% if is_incremental() %}
    -- Só processa pedidos mais recentes que o último já carregado
    WHERE o.order_date > (SELECT MAX(order_date) FROM {{ this }})
{% endif %}
