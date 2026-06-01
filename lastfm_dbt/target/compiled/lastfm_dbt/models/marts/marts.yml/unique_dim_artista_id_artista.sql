
    
    

select
    id_artista as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."dim_artista"
where id_artista is not null
group by id_artista
having count(*) > 1


