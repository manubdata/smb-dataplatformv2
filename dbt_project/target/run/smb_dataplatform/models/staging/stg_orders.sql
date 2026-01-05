

  create or replace view `smb-dataplatform`.`smb_dataplatform`.`stg_orders`
  OPTIONS()
  as -- Silver Layer (staging) for Orders
-- This model cleans and prepares raw order data from the bronze layer.

with source as (
    -- This should point to your raw orders data in the bronze layer
    select * from `smb-dataplatform`.`shopify_data`.`orders`
)

select
    id as order_id,
    customer__id as customer_id,
    cast(created_at as date) as order_date,
    cast(total_price as numeric(38, 2)) as net_sales,
    
    -- Mock COGS as 50% of net sales. In a real scenario, this would come from
    -- product cost data.
    cast(total_price as numeric(38, 2)) * 0.50 as cogs,
    
    -- Extracting shipping cost from the nested field.
    cast(total_shipping_price_set__shop_money__amount as numeric(38, 2)) as shipping_cost,
    
    -- Transaction Fee is a placeholder. This often comes from a separate
    -- payment gateway source (e.g., Stripe, Shopify Payments).
    0 as transaction_fee

from source;

