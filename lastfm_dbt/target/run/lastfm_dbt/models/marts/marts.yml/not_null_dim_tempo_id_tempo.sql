
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_tempo
from "lastfm_charts"."public"."dim_tempo"
where id_tempo is null



  
  
      
    ) dbt_internal_test