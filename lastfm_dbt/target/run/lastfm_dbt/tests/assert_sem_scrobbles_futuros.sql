
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  -- teste singular: nenhum scrobble pode ter timestamp no futuro
-- se essa query retornar linhas, o teste falha

SELECT
    id_tempo
    ,id_usuario
FROM "lastfm_charts"."public"."fact_scrobbles"
WHERE id_tempo > EXTRACT(EPOCH FROM NOW())::BIGINT
  
  
      
    ) dbt_internal_test