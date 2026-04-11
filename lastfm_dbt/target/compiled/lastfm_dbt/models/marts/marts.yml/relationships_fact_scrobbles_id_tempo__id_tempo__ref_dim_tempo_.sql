
    
    

with child as (
    select id_tempo as from_field
    from "lastfm_charts"."public"."fact_scrobbles"
    where id_tempo is not null
),

parent as (
    select id_tempo as to_field
    from "lastfm_charts"."public"."dim_tempo"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


