
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select artist_name
from "lastfm_charts"."public"."stg_scrobbles"
where artist_name is null



  
  
      
    ) dbt_internal_test