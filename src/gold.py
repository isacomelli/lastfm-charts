# %% [markdown]
# ### CAMADA GOLD - Star Schema no PostgreSQL
# Lê o Parquet da Silver e carrega nas tabelas dimensão + fato do Postgres.
# 
# Star Schema:
#    dim_usuario    - quem escutou
#    dim_artista    - artista da faixa
#    dim_album      - álbum
#    dim_faixa      - faixa musical
#    dim_tempo      - dimensão de datas (granularidade: hora)
#    fact_scrobbles - tabela fato (chaves + métricas)
# 
# Métricas de negócio (5 queries ao final):
#    1. Ranking geral de artistas do grupo
#    2. Quem escutou mais música (por usuário)
#    3. Artista mais escutado por usuário
#    4. Hora do dia com mais scrobbles
#    5. Top 10 faixas do grupo

# %%
import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# %%
PARQUET_PATH = os.path.join('data', 'silver', 'silver.parquet')

DB_URL = (
    f'postgresql+psycopg2://'
    f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}"
    f"/{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DB_URL)

# %% [markdown]
# #### Leitura da Silver

# %%
print('Lendo Silver...')
df = pd.read_parquet(PARQUET_PATH)
print(f'  Shape: {df.shape}')

# %% [markdown]
# #### Criar Schema

# %%
DDL = '''
CREATE TABLE IF NOT EXISTS dim_usuario (
    id_usuario     SERIAL PRIMARY KEY
    ,username       VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_artista (
    id_artista     SERIAL PRIMARY KEY
    ,artist_name    VARCHAR(500) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_album (
    id_album       SERIAL PRIMARY KEY
    ,album_name     VARCHAR(500) NOT NULL
    ,id_artista     INT REFERENCES dim_artista(id_artista)
    ,UNIQUE (album_name, id_artista)
);

CREATE TABLE IF NOT EXISTS dim_faixa (
    id_faixa       SERIAL PRIMARY KEY
    ,track_name     VARCHAR(500) NOT NULL
    ,title          VARCHAR(1000)
    ,id_artista     INT REFERENCES dim_artista(id_artista)
    ,id_album       INT REFERENCES dim_album(id_album)
    ,UNIQUE (track_name, id_artista)
);

CREATE TABLE IF NOT EXISTS dim_tempo (
    id_tempo       BIGINT PRIMARY KEY  -- timestamp_unix como PK
    ,datetime_utc   TIMESTAMPTZ
    ,ano            SMALLINT
    ,mes            SMALLINT
    ,nome_mes       VARCHAR(20)
    ,dia            SMALLINT
    ,hora           SMALLINT
    ,dia_semana     SMALLINT
    ,nome_dia       VARCHAR(20)
    ,semana_ano     SMALLINT
    ,trimestre      SMALLINT
    ,semestre       SMALLINT
);

CREATE TABLE IF NOT EXISTS fact_scrobbles (
    id_scrobble    SERIAL PRIMARY KEY
    ,id_usuario     INT REFERENCES dim_usuario(id_usuario)
    ,id_faixa       INT REFERENCES dim_faixa(id_faixa)
    ,id_artista     INT REFERENCES dim_artista(id_artista)
    ,id_album       INT REFERENCES dim_album(id_album)
    ,id_tempo       BIGINT REFERENCES dim_tempo(id_tempo)
    ,scrobbles      SMALLINT DEFAULT 1
);
'''

with engine.connect() as conn:
    conn.execute(text(DDL))
    conn.commit()
print('Schema criado')

with engine.connect() as conn:
    conn.execute(text('''
        TRUNCATE fact_scrobbles, dim_tempo, dim_faixa, dim_album, dim_artista, dim_usuario 
        RESTART IDENTITY CASCADE;
        '''))
    conn.commit()
print('Tabelas limpas')

# %% [markdown]
# #### Função auxiliar de upsert via pandas

# %%
def load_dim(df_dim: pd.DataFrame, table: str, unique_col: str, engine) -> pd.DataFrame:
    '''
    Insere registros novos na dimensão e retorna o DataFrame com a coluna de ID preenchida.
    '''
    df_dim = df_dim.drop_duplicates(subset=[unique_col]).copy()
    df_dim.to_sql(table, engine, if_exists='append', index=False, method='multi', chunksize=1000)

    id_col = f"id_{table.replace('dim_', '')}"
    df_ids = pd.read_sql(f'SELECT {id_col}, {unique_col} FROM {table}', engine)
    return df_ids

# %% [markdown]
# #### Carregar Dimensões

# %%
## dim_usuario
print('Carregando dim_usuario...')
df_usuarios = df[['username']].drop_duplicates()
try:
    df_usuarios.to_sql('dim_usuario', engine, if_exists='append', index=False, method='multi')
except Exception as e:
    print(f'  Erro dim_usuario: {e}')

df_usr_ids = pd.read_sql('SELECT id_usuario, username FROM dim_usuario', engine)

## dim_artista
print('Carregando dim_artista...')
df_artistas = df[['artist_name']].drop_duplicates()
try:
    df_artistas.to_sql('dim_artista', engine, if_exists='append', index=False, method='multi')
except Exception:
    pass
df_art_ids = pd.read_sql('SELECT id_artista, artist_name FROM dim_artista', engine)

## dim_album (precisa do id_artista)
print('Carregando dim_album...')
df_albums = (df[['album_name', 'artist_name']]
            .drop_duplicates()
            .merge(df_art_ids, on='artist_name')
            .drop(columns=['artist_name']))
try:
    df_albums.to_sql('dim_album', engine, if_exists='append', index=False, method='multi')
except Exception:
    pass
df_alb_ids = pd.read_sql('SELECT id_album, album_name, id_artista FROM dim_album', engine)

## dim_faixa
print('Carregando dim_faixa...')
df_faixas = (df[['track_name', 'title', 'artist_name', 'album_name']]
            .drop_duplicates(subset=['track_name', 'artist_name'])
            .merge(df_art_ids, on='artist_name')
            .merge(df_alb_ids[['id_album', 'album_name', 'id_artista']], on=['album_name', 'id_artista'], how='left')
            .drop(columns=['artist_name', 'album_name']))
try:
    df_faixas.to_sql('dim_faixa', engine, if_exists='append', index=False, method='multi')
except Exception:
    pass
df_fax_ids = pd.read_sql('SELECT id_faixa, track_name, id_artista FROM dim_faixa', engine)

## dim_tempo
print('Carregando dim_tempo...')
df_tempo = (df[['timestamp_unix', 'datetime_utc', 'year', 'month', 'month_name',
                'day', 'hour', 'weekday', 'weekday_name', 'week_of_year',
                'quarter', 'semester']]
            .drop_duplicates(subset=['timestamp_unix'])
            .rename(columns={
                'timestamp_unix': 'id_tempo'
                ,'year'         : 'ano'
                ,'month'        : 'mes'
                ,'month_name'   : 'nome_mes'
                ,'day'          : 'dia'
                ,'hour'         : 'hora'
                ,'weekday'      : 'dia_semana'
                ,'weekday_name' : 'nome_dia'
                ,'week_of_year' : 'semana_ano'
                ,'quarter'      : 'trimestre'
                ,'semester'     : 'semestre'
            }))
try:
    df_tempo.to_sql('dim_tempo', engine, if_exists='append', index=False, method='multi', chunksize=5000)
except Exception:
    pass

# %% [markdown]
# #### Carregar Fato

# %%
print('Carregando fact_scrobbles...')

df_fact = (df[['username', 'track_name', 'artist_name', 'album_name', 'timestamp_unix']]
          .merge(df_usr_ids, on='username')
          .merge(df_art_ids, on='artist_name')
          .merge(df_alb_ids[['id_album', 'album_name', 'id_artista']], on=['album_name', 'id_artista'], how='left')
          .merge(df_fax_ids, on=['track_name', 'id_artista'], how='left')
          .rename(columns={'timestamp_unix': 'id_tempo'})
          [['id_usuario', 'id_faixa', 'id_artista', 'id_album', 'id_tempo']])

df_fact['scrobbles'] = 1

df_fact.to_sql('fact_scrobbles', engine, if_exists='append', index=False, method='multi', chunksize=10000)
print(f'  {len(df_fact):,} linhas inseridas em fact_scrobbles')

# %% [markdown]
# #### Métricas de Negócio

# %%
QUERIES = {
    '1. Ranking geral de artistas do grupo': '''
        SELECT 
            a.artist_name     AS artista
            ,SUM(f.scrobbles) AS total_scrobbles
        FROM fact_scrobbles AS f
        
        JOIN dim_artista AS a 
            ON f.id_artista = a.id_artista
        
        GROUP  BY artista
        
        ORDER  BY total_scrobbles DESC
        LIMIT  10;
    ''',

    '2. Quem escutou mais música (por usuário)': '''
        SELECT
            u.username
            ,SUM(f.scrobbles) AS total_scrobbles
        FROM fact_scrobbles AS f
        
        JOIN dim_usuario AS u
            ON f.id_usuario = u.id_usuario
        
        GROUP BY u.username
        
        ORDER BY total_scrobbles DESC;
    ''',

    '3. Artista favorito por usuário': '''
        SELECT
            username
            ,artista_favorito
            ,scrobbles
        FROM (
            SELECT
                u.username
                ,a.artist_name    AS artista_favorito
                ,SUM(f.scrobbles) AS scrobbles
                ,ROW_NUMBER() OVER (PARTITION BY u.username ORDER BY SUM(f.scrobbles) DESC) AS rn
            FROM fact_scrobbles AS f
            
            JOIN dim_usuario AS u
                ON f.id_usuario = u.id_usuario
            JOIN dim_artista AS a
                ON f.id_artista = a.id_artista
            
            GROUP BY u.username, a.artist_name
        ) sub
        WHERE rn = 1;
    ''',

    '4. Hora do dia com mais scrobbles': '''
        SELECT
            t.hora
            ,SUM(f.scrobbles) AS total_scrobbles
        FROM fact_scrobbles AS f
        
        JOIN dim_tempo AS t
            ON f.id_tempo = t.id_tempo
        
        GROUP BY t.hora
        
        ORDER BY total_scrobbles DESC;
    ''',

    '5. Top 10 faixas do grupo': '''
        SELECT
            fx.track_name     AS faixa
            ,a.artist_name    AS artista
            ,SUM(f.scrobbles) AS total_scrobbles
        FROM fact_scrobbles AS f
        
        JOIN dim_faixa AS fx
            ON f.id_faixa = fx.id_faixa
        JOIN dim_artista AS a  
            ON f.id_artista = a.id_artista
        
        GROUP  BY faixa, artista
        
        ORDER  BY total_scrobbles DESC
        LIMIT  10;
    ''',
}

print('\n' + '─' * 60)
print('MÉTRICAS DE NEGÓCIO')
print('─' * 60)

with engine.connect() as conn:
    for title, query in QUERIES.items():
        print(f'\n▶ {title}')
        try:
            result = pd.read_sql(text(query), conn)
            print(result.to_string(index=False))
        except Exception as e:
            print(f'  Erro: {e}')

print('\nGold concluída.')