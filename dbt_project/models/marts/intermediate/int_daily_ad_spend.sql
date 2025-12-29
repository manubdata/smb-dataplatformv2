{{ config(materialized='table') }}

with meta_insights as (
    select
        date_day,
        spend,
        publisher_platform
    from {{ ref('stg_meta_ads') }}
),
tiktok_spend as (
    select
        date_day,
        spend
    from {{ ref('stg_tiktok_ads') }}
),
daily_meta_platform_spend as (
    select
        date_day,
        sum(case when lower(publisher_platform) = 'facebook' then spend else 0 end) as facebook_spend,
        sum(case when lower(publisher_platform) = 'instagram' then spend else 0 end) as instagram_spend,
        sum(spend) as meta_total_spend
    from meta_insights
    group by 1
)
select
    coalesce(dmp.date_day, ts.date_day) as date_day,
    coalesce(dmp.meta_total_spend, 0) + coalesce(ts.spend, 0) as total_ad_spend,
    coalesce(dmp.facebook_spend, 0) as facebook_spend,
    coalesce(dmp.instagram_spend, 0) as instagram_spend,
    coalesce(ts.spend, 0) as tiktok_spend
from daily_meta_platform_spend dmp
full outer join tiktok_spend ts on dmp.date_day = ts.date_day