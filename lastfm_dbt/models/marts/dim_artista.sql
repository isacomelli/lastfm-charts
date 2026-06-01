-- dimensão de artistas

SELECT DISTINCT
    {{ gerar_chave_surrogate('artist_name') }} AS id_artista
    ,artist_name
FROM {{ ref('stg_scrobbles') }}
