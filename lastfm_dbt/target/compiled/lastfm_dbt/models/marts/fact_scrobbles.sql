-- tabela fato: cada linha é um scrobble (evento de escuta)
-- granularidade: 1 linha por scrobble
-- row_number() garante id_scrobble único mesmo se houver timestamps repetidos

WITH base AS (

    SELECT
        username
        ,track_name
        ,artist_name
        ,album_name
        ,timestamp_unix
        ,ROW_NUMBER() OVER (
            PARTITION BY username, timestamp_unix
            ORDER BY track_name
        ) AS rn
    FROM "lastfm_charts"."public"."stg_scrobbles"

),

dedup AS (

    SELECT * FROM base WHERE rn = 1

)

SELECT
    

MD5(CAST(usr.id_usuario AS TEXT) || '|' || CAST(d.timestamp_unix AS TEXT))

 AS id_scrobble
    ,usr.id_usuario
    ,fax.id_faixa
    ,art.id_artista
    ,alb.id_album
    ,d.timestamp_unix                                                  AS id_tempo
    ,1::SMALLINT                                                       AS scrobbles
FROM dedup AS d
INNER JOIN "lastfm_charts"."public"."dim_usuario" AS usr
    ON d.username    = usr.username
INNER JOIN "lastfm_charts"."public"."dim_artista" AS art
    ON d.artist_name = art.artist_name
LEFT JOIN "lastfm_charts"."public"."dim_album" AS alb
    ON  d.album_name  = alb.album_name
    AND art.id_artista = alb.id_artista
LEFT JOIN "lastfm_charts"."public"."dim_faixa" AS fax
    ON  d.track_name  = fax.track_name
    AND art.id_artista = fax.id_artista