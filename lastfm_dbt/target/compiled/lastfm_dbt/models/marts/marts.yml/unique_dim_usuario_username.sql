
    
    

select
    username as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."dim_usuario"
where username is not null
group by username
having count(*) > 1


