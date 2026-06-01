-- teste singular: nenhum scrobble pode ter timestamp no futuro
-- se essa query retornar linhas, o teste falha

SELECT
    id_tempo
    ,id_usuario
FROM {{ ref('fact_scrobbles') }}
WHERE id_tempo > EXTRACT(EPOCH FROM NOW())::BIGINT
