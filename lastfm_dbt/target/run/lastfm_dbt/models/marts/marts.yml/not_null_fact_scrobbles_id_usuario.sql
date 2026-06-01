
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_usuario
from "lastfm_charts"."public"."fact_scrobbles"
where id_usuario is null



  
  
      
    ) dbt_internal_test