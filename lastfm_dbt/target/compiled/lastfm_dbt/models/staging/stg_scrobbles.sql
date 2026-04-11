-- leitura da silver com casting explícito de tipos
-- filtra registros sem timestamp, usuário, faixa ou artista

WITH source AS (

    SELECT * FROM "lastfm_charts"."silver"."scrobbles"

),

staged AS (

    SELECT
        username::VARCHAR                         AS username
        ,track_name::VARCHAR                      AS track_name
        ,artist_name::VARCHAR                     AS artist_name
        ,COALESCE(album_name, 'Unknown')::VARCHAR AS album_name
        ,title::VARCHAR                           AS title
        ,timestamp_unix::BIGINT                   AS timestamp_unix
        ,datetime_utc::TIMESTAMPTZ                AS datetime_utc
        ,year::SMALLINT                           AS year
        ,month::SMALLINT                          AS month
        ,month_name::VARCHAR                      AS month_name
        ,day::SMALLINT                            AS day
        ,hour::SMALLINT                           AS hour
        ,weekday::SMALLINT                        AS weekday
        ,weekday_name::VARCHAR                    AS weekday_name
        ,week_of_year::SMALLINT                   AS week_of_year
        ,quarter::SMALLINT                        AS quarter
        ,semester::SMALLINT                       AS semester

    FROM source
    WHERE timestamp_unix IS NOT NULL
      AND username        IS NOT NULL
      AND track_name      IS NOT NULL
      AND artist_name     IS NOT NULL

)

SELECT * FROM staged