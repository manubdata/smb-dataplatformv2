
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select date_day
from `smb-dataplatform`.`smb_dataplatform`.`int_daily_ad_spend`
where date_day is null



  
  
      
    ) dbt_internal_test