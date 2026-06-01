
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_scrobble
from "lastfm_charts"."public"."fact_scrobbles"
where id_scrobble is null



  
  
      
    ) dbt_internal_test