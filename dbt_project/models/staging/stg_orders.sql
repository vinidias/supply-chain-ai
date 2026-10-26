{{ config(materialized="view", schema="staging") }}

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
FROM {{ source('raw', 'orders') }} o
LEFT JOIN {{ source('raw', 'products') }} p ON p.id = o.product_id
