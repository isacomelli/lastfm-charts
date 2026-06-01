
  
    

  create  table "lastfm_charts"."public"."dim_album__dbt_tmp"
  
  
    as
  
  (
    -- dimensão de álbuns
-- chave natural: (album_name, id_artista) — mesmo nome pode ter artistas diferentes

WITH albums AS (

    SELECT DISTINCT
        album_name
        ,artist_name
    FROM "lastfm_charts"."public"."stg_scrobbles"

)

SELECT
    

MD5(CAST(a.album_name AS TEXT) || '|' || CAST(art.id_artista AS TEXT))

 AS id_album
    ,a.album_name
    ,art.id_artista
FROM albums AS a
INNER JOIN "lastfm_charts"."public"."dim_artista" AS art
    ON a.artist_name = art.artist_name
  );
  