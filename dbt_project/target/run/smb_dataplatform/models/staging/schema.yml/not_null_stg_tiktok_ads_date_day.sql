
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select date_day
from "dbt_metrics"."main"."stg_tiktok_ads"
where date_day is null



  
  
      
    ) dbt_internal_test