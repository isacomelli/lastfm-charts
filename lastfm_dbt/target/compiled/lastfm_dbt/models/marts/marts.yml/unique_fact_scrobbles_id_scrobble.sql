
    
    

select
    id_scrobble as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."fact_scrobbles"
where id_scrobble is not null
group by id_scrobble
having count(*) > 1


