-- dimensão de usuários do grupo

SELECT DISTINCT
    {{ gerar_chave_surrogate('username') }} AS id_usuario
    ,username
FROM {{ ref('stg_scrobbles') }}
