
    
    

with dbt_test__target as (

  select date_day as unique_field
  from `smb-dataplatform`.`smb_dataplatform`.`int_daily_ad_spend`
  where date_day is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


