
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select username
from "lastfm_charts"."public"."dim_usuario"
where username is null



  
  
      
    ) dbt_internal_test