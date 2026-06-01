
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_tempo as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."dim_tempo"
where id_tempo is not null
group by id_tempo
having count(*) > 1



  
  
      
    ) dbt_internal_test