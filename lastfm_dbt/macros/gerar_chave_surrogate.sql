{% macro gerar_chave_surrogate() %}

{#
    Gera uma chave surrogate via MD5 sobre a concatenação de uma ou mais colunas.
    Uso: {{ gerar_chave_surrogate('coluna_a') }}
         {{ gerar_chave_surrogate('coluna_a', 'coluna_b') }}
#}

    {%- set colunas = varargs -%}

    MD5(
        {%- for col in colunas -%}
            CAST({{ col }} AS TEXT)
            {%- if not loop.last %} || '|' || {% endif %}
        {%- endfor -%}
    )

{% endmacro %}
