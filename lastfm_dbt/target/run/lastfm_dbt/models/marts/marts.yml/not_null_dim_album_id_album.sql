
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_album
from "lastfm_charts"."public"."dim_album"
where id_album is null



  
  
      
    ) dbt_internal_test