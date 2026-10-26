{{ config(materialized="view", schema="staging") }}

SELECT
    p.id AS product_id,
    p.name AS product_name,
    p.category,
    p.unit_cost,
    p.lead_time_days,
    s.id AS supplier_id,
    s.name AS supplier_name,
    s.country AS supplier_country,
    s.rating AS supplier_rating
FROM products p
LEFT JOIN suppliers s ON s.id = p.supplier_id
