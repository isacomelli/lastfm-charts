
  
    

  create  table "lastfm_charts"."public"."dim_usuario__dbt_tmp"
  
  
    as
  
  (
    -- dimensão de usuários do grupo

SELECT DISTINCT
    

MD5(CAST(username AS TEXT))

 AS id_usuario
    ,username
FROM "lastfm_charts"."public"."stg_scrobbles"
  );
  