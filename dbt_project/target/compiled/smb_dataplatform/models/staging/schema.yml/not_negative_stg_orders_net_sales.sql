

select *
from "dbt_metrics"."main"."stg_orders"
where net_sales < 0

