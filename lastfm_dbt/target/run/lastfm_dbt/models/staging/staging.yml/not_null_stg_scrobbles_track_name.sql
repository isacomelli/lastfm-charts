
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select track_name
from "lastfm_charts"."public"."stg_scrobbles"
where track_name is null



  
  
      
    ) dbt_internal_test