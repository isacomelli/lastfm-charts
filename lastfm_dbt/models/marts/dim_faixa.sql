-- dimensão de faixas musicais
-- chave natural: (track_name, id_artista)
-- distinct apenas nas colunas da chave natural para evitar duplicatas
-- quando a mesma faixa aparece com álbuns diferentes

WITH faixas AS (

    SELECT DISTINCT
        track_name
        ,artist_name
    FROM {{ ref('stg_scrobbles') }}

),

com_album AS (

    -- pega um álbum por faixa (min() garante unicidade)
    SELECT
        track_name
        ,artist_name
        ,MIN(album_name) AS album_name
    FROM {{ ref('stg_scrobbles') }}
    GROUP BY track_name, artist_name

)

SELECT
    {{ gerar_chave_surrogate('f.track_name', 'art.id_artista') }} AS id_faixa
    ,f.track_name
    ,f.track_name || ' - ' || f.artist_name                       AS title
    ,art.id_artista
    ,alb.id_album
FROM faixas AS f
INNER JOIN {{ ref('dim_artista') }} AS art
    ON f.artist_name = art.artist_name
LEFT JOIN com_album AS ca
    ON  f.track_name  = ca.track_name
    AND f.artist_name = ca.artist_name
LEFT JOIN {{ ref('dim_album') }} AS alb
    ON  ca.album_name  = alb.album_name
    AND art.id_artista = alb.id_artista
