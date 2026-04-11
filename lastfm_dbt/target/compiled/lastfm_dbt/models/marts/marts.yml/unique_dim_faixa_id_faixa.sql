
    
    

select
    id_faixa as unique_field,
    count(*) as n_records

from "lastfm_charts"."public"."dim_faixa"
where id_faixa is not null
group by id_faixa
having count(*) > 1


