
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select publisher_platform
from "dbt_metrics"."main"."stg_meta_ads"
where publisher_platform is null



  
  
      
    ) dbt_internal_test