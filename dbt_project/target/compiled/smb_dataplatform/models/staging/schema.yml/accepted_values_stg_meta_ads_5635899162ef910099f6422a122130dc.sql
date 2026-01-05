
    
    

with all_values as (

    select
        publisher_platform as value_field,
        count(*) as n_records

    from `smb-dataplatform`.`smb_dataplatform`.`stg_meta_ads`
    group by publisher_platform

)

select *
from all_values
where value_field not in (
    'facebook','instagram'
)


