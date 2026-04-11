
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    id_album as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."dim_album"
where id_album is not null
group by id_album
having count(*) > 1



  
  
      
    ) dbt_internal_test