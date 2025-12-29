
  
  create view "dbt_metrics"."main"."stg_tiktok_ads__dbt_tmp" as (
    -- Silver Layer (staging) for TikTok Ads
-- This model cleans and prepares raw ad spend data from the bronze layer.

with source as (
    -- This should point to your raw tiktok ads data in the bronze layer
    select
        cast(stat_time_day as date) as date_day,
        spend
    from "tiktok_db"."main"."ad_reports"
)

select
    date_day,
    sum(spend) as spend -- Aggregate spend by date_day to ensure uniqueness
from source
group by 1
  );
