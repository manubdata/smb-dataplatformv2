
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    date_day as unique_field,
    count(*) as n_records

from "dbt_metrics"."main"."int_daily_orders"
where date_day is not null
group by date_day
having count(*) > 1



  
  
      
    ) dbt_internal_test