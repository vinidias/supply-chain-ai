{{ config(materialized="view", schema="staging") }}

SELECT
    id AS supplier_id,
    name AS supplier_name,
    country,
    category,
    rating
FROM {{ source('raw', 'suppliers') }}
