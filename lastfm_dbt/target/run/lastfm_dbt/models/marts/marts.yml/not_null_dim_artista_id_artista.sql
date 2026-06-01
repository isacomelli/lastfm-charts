
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_artista
from "lastfm_charts"."public"."dim_artista"
where id_artista is null



  
  
      
    ) dbt_internal_test