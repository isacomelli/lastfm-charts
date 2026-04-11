
    
    

select
    id_usuario as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."dim_usuario"
where id_usuario is not null
group by id_usuario
having count(*) > 1


