-- tests/assert_gmv_positive.sql
-- Falha se algum supplier tiver gmv < 0
SELECT *
FROM {{ ref('mart_supplier_performance') }}
WHERE gmv < 0
