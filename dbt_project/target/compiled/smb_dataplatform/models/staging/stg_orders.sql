-- Silver Layer (staging) for Orders
-- This model cleans and prepares raw order data from the bronze layer.

with source as (
    -- This should point to your raw orders data in the bronze layer
    select * from "shopify_db"."shopify_data"."orders"
)

select
    id as order_id,
    customer__id as customer_id,
    cast(created_at as date) as order_date,
    financial_status,

    -- Net Sales is total price minus discounts.
    cast(total_price as numeric) - cast(total_discounts as numeric) as net_sales,
    
    -- Mock COGS as 50% of net sales. In a real scenario, this would come from
    -- product cost data.
    cast(total_line_items_price as numeric) * 0.50 as cogs,
    
    -- Extracting shipping cost from the nested field.
    cast(total_shipping_price_set__shop_money__amount as numeric) as shipping_cost,

    cast(total_discounts as numeric) as total_discounts,
    
    -- Transaction Fee is a placeholder. This often comes from a separate
    -- payment gateway source (e.g., Stripe, Shopify Payments).
    0 as transaction_fee,

    total_line_items_price,

    product_id,
    product_title,
    product_quantity,
    product_price

from source