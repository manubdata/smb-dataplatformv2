
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select publisher_platform
from `smb-dataplatform`.`smb_dataplatform`.`stg_meta_ads`
where publisher_platform is null



  
  
      
    ) dbt_internal_test