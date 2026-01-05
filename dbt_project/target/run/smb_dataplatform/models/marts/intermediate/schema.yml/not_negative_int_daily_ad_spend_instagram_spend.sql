
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  

select *
from `smb-dataplatform`.`smb_dataplatform`.`int_daily_ad_spend`
where instagram_spend < 0


  
  
      
    ) dbt_internal_test