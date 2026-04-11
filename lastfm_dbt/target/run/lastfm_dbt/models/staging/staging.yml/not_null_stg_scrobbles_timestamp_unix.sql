
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select timestamp_unix
from "lastfm_charts"."public"."stg_scrobbles"
where timestamp_unix is null



  
  
      
    ) dbt_internal_test