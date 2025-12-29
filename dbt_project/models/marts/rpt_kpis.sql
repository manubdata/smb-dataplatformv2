{{ config(materialized='table') }}

with daily_orders as (
    select * from {{ ref('int_daily_orders') }}
),
daily_ad_spend as (
    select * from {{ ref('int_daily_ad_spend') }}
),
final_data as (
    select
        coalesce(d.date_day, ads.date_day) as date_day,
        coalesce(d.total_net_sales, 0) as total_net_sales,
        coalesce(d.total_cogs, 0) as total_cogs,
        coalesce(d.total_shipping_cost, 0) as total_shipping_cost,
        coalesce(d.total_transaction_fee, 0) as total_transaction_fee,
        coalesce(ads.total_ad_spend, 0) as total_ad_spend,
        coalesce(ads.facebook_spend, 0) as facebook_spend,
        coalesce(ads.instagram_spend, 0) as instagram_spend,
        coalesce(ads.tiktok_spend, 0) as tiktok_spend,
        coalesce(d.total_orders, 0) as total_orders,
        coalesce(d.first_time_orders, 0) as first_time_orders,
        coalesce(d.total_customers, 0) as total_customers
    from daily_orders d
    full outer join daily_ad_spend ads on d.date_day = ads.date_day
)
select
    date_day,
    total_net_sales,
    total_ad_spend,
    facebook_spend,
    instagram_spend,
    tiktok_spend,
    
    -- Contribution Margin: Net Sales - COGS - Shipping - Transaction Fees - Total Ad Spend
    (total_net_sales - total_cogs - total_shipping_cost - total_transaction_fee - total_ad_spend) as contribution_margin,
    
    -- Marketing Efficiency Ratio (MER)
    {{ safe_divide('total_net_sales', '(facebook_spend + instagram_spend + tiktok_spend)') }} as mer_total_paid_ads,
    
    -- MER for Facebook only
    {{ safe_divide('total_net_sales', 'facebook_spend') }} as mer_facebook,
    
    -- MER for Instagram only
    {{ safe_divide('total_net_sales', 'instagram_spend') }} as mer_instagram,
    
    -- New Customer Cost Per Acquisition (ncCPA): Total Ad Spend / Count(First Time Orders)
    {{ safe_divide('total_ad_spend', 'first_time_orders') }} as nc_cpa,
    
    -- Net Profit on Ad Spend (NPOAS): Contribution Margin / Total Ad Spend
    {{ safe_divide('(total_net_sales - total_cogs - total_shipping_cost - total_transaction_fee - total_ad_spend)', 'total_ad_spend') }} as npoas,
    
    -- LTV:CAC Ratio: ((Avg Order Value * Purchase Freq) / ncCPA)
    -- LTV is a simplified version: Avg Order Value * Purchase Freq
    -- CAC is ncCPA from above
    {{ safe_divide(
        '(' ~ safe_divide('total_net_sales', 'total_orders') ~ ' * ' ~ safe_divide('total_orders', 'total_customers') ~ ')',
        safe_divide('total_ad_spend', 'first_time_orders')
    ) }} as ltv_cac_ratio
    
from final_data
order by date_day desc