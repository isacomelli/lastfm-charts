
    
    

select
    artist_name as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."dim_artista"
where artist_name is not null
group by artist_name
having count(*) > 1


