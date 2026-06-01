
  
    

  create  table "lastfm_charts"."public"."dim_artista__dbt_tmp"
  
  
    as
  
  (
    -- dimensão de artistas

SELECT DISTINCT
    

MD5(CAST(artist_name AS TEXT))

 AS id_artista
    ,artist_name
FROM "lastfm_charts"."public"."stg_scrobbles"
  );
  