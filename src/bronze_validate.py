# ### Validação de Dados com Great Expectations
# Roda após a Bronze e antes da Silver.
# Valida o bronze.csv e gera o relatório HTML (Data Docs).

import pandas as pd
import great_expectations as gx
from datetime import datetime

BRONZE_PATH = 'data/bronze/bronze.csv'

# Mesmo padrão do bronze.py
FROM_TIMESTAMP = int(datetime.strptime('2004-01-01', '%Y-%m-%d').timestamp())
NOW_TIMESTAMP  = int(pd.Timestamp.now(tz='UTC').timestamp())

# Leitura
print('Lendo Bronze...')
df = pd.read_csv(BRONZE_PATH, low_memory=False)
print(f'  {len(df):,} linhas | {len(df.columns)} colunas')

# Contexto GX
print('\nInicializando Great Expectations...')
context = gx.get_context(context_root_dir='data/gx')

data_source = context.data_sources.add_or_update_pandas('bronze')
data_asset  = data_source.add_dataframe_asset('bronze_csv')
batch_def   = data_asset.add_batch_definition_whole_dataframe('bronze_batch')

suite = context.suites.add_or_update(gx.ExpectationSuite(name='bronze_suite'))

# 1. Colunas essenciais existem
#    A Silver renomeia:
#        name          → track_name
#        artist.#text  → artist_name
#        album.#text   → album_name
#        date.uts      → timestamp_unix
#        _display_name → username

for col in ['name', 'artist.#text', 'album.#text', 'date.uts', '_display_name']:
    suite.add_expectation(
        gx.expectations.ExpectColumnToExist(column=col)
    )

# 2. date.uts (→ timestamp_unix) não pode ser nulo
#    Scrobbles sem timestamp são descartados na Silver, queremos saber o volume aqui
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(column='date.uts')
)

# 3. _display_name (→ username) não pode ser nulo
#    Todo scrobble precisa estar associado a um usuário do grupo
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column='_display_name',
    )
)

# 4. date.uts (→ timestamp_unix) deve ser numérico (timestamp Unix como string)
#    A Silver faz pd.to_numeric() nessa coluna, valores não numéricos viram NaN
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToMatchRegex(
        column='date.uts',
        regex=r'^\d+$',
    )
)

# 5. date.#text (→ datetime_raw) deve seguir o formato da API do Last.fm: 'DD Mon YYYY, HH:MM'
#    Ex: '01 Jan 2004, 00:00'
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToMatchRegex(
        column='date.#text',
        regex=r'^\d{2} \w{3} \d{4}, \d{2}:\d{2}$',
    )
)

# 6. date.uts (→ timestamp_unix) deve estar dentro do intervalo válido (2004 → hoje)
#    Valores fora desse range indicam dados corrompidos ou nowplaying não filtrado
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column='date.uts',
        min_value=str(FROM_TIMESTAMP),
        max_value=str(NOW_TIMESTAMP),
    )
)

# 7. name (→ track_name) não pode ser nulo
#    Scrobble sem nome de faixa não tem valor analítico
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(column='name')
)

# 8. artist.#text (→ artist_name) não pode ser nulo
#    Sem artista não é possível fazer joins nas dimensões Gold
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(column='artist.#text')
)

# 9. O dataset deve ter pelo menos 1 milhão de linhas
#    Requisito do laboratório e sinal de que a coleta foi completa
suite.add_expectation(
    gx.expectations.ExpectTableRowCountToBeBetween(min_value=1_000_000)
)

# Validação
print('\nValidando...')
definition = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(
        name='bronze_validation',
        data=batch_def,
        suite=suite,
    )
)
results = definition.run(batch_parameters={'dataframe': df})

# Data Docs
context.build_data_docs()
print('Data Docs gerados em: data/gx/ignore/data_docs/local_site/index.html')

# Resultado
print(f"\n{'Validação passou' if results.success else 'Validação falhou'}")
print('─' * 60)
for result in results.results:
    status = '[PASSOU]' if result.success else '[FALHOU]'
    exp    = result.expectation_config.type
    col    = result.expectation_config.kwargs.get('column', 'tabela')
    print(f'  {status}  {exp:<50} [{col}]')