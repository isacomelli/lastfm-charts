
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_faixa as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."dim_faixa"
where id_faixa is not null
group by id_faixa
having count(*) > 1



  
  
      
    ) dbt_internal_test