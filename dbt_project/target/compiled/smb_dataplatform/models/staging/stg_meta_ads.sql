-- Silver Layer (staging) for Meta Ads
-- This model cleans and prepares raw ad spend data from the bronze layer.

with source as (
    -- This should point to your raw meta ads data in the bronze layer
    select * from `smb-dataplatform`.`facebook_ads_data`.`ads_insights`
)

select
    cast(date_start as date) as date_day,
    spend,
    publisher_platform
from source