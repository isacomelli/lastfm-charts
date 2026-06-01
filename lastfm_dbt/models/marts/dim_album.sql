-- dimensão de álbuns
-- chave natural: (album_name, id_artista) — mesmo nome pode ter artistas diferentes

WITH albums AS (

    SELECT DISTINCT
        album_name
        ,artist_name
    FROM {{ ref('stg_scrobbles') }}

)

SELECT
    {{ gerar_chave_surrogate('a.album_name', 'art.id_artista') }} AS id_album
    ,a.album_name
    ,art.id_artista
FROM albums AS a
INNER JOIN {{ ref('dim_artista') }} AS art
    ON a.artist_name = art.artist_name
