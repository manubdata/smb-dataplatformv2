
    
    

with all_values as (

    select
        publisher_platform as value_field,
        count(*) as n_records

    from "dbt_metrics"."main"."stg_meta_ads"
    group by publisher_platform

)

select *
from all_values
where value_field not in (
    'facebook','instagram'
)


