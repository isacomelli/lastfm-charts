-- dimensão de tempo, granularidade por hora
-- timestamp_unix é a PK natural — único por definição

SELECT DISTINCT
    timestamp_unix  AS id_tempo
    ,datetime_utc
    ,year           AS ano
    ,month          AS mes
    ,month_name     AS nome_mes
    ,day            AS dia
    ,hour           AS hora
    ,weekday        AS dia_semana
    ,weekday_name   AS nome_dia
    ,week_of_year   AS semana_ano
    ,quarter        AS trimestre
    ,semester       AS semestre
FROM {{ ref('stg_scrobbles') }}
