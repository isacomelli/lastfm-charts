
    
    

with child as (
    select id_artista as from_field
    from "lastfm_charts"."public"."dim_faixa"
    where id_artista is not null
),

parent as (
    select id_artista as to_field
    from "lastfm_charts"."public"."dim_artista"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


