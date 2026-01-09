
  
    
    

    create  table
      "dbt_metrics"."main"."int_daily_orders__dbt_tmp"
  
    as (
      

with orders as (
    select * from "dbt_metrics"."main"."stg_orders"
),
customer_order_rank as (
    select
        order_id,
        customer_id,
        order_date,
        rank() over (partition by customer_id order by order_date, order_id) as customer_order_rank
    from orders
),
orders_with_rank as (
    select
        o.*,
        cor.customer_order_rank
    from orders o
    join customer_order_rank cor on o.order_id = cor.order_id
)
select
    order_date as date_day,
    product_id,
    product_title,

    sum(net_sales) as total_net_sales,
    sum(cogs) as total_cogs,
    sum(shipping_cost) as total_shipping_cost,
    sum(transaction_fee) as total_transaction_fee,
    sum(total_discounts) as total_discounts,
    
    sum(product_price * product_quantity) as product_revenue,
    sum(product_price * product_quantity * 0.5) as product_cogs, -- Mock COGS
    sum(product_quantity) as product_quantity,

    count(distinct order_id) as total_orders,
    count(case when customer_order_rank = 1 then order_id end) as first_time_orders,
    count(distinct customer_id) as total_customers
from orders_with_rank
group by 1,2,3
    );
  
  