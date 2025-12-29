
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  

select *
from "dbt_metrics"."main"."rpt_kpis"
where ltv_cac_ratio < 0


  
  
      
    ) dbt_internal_test