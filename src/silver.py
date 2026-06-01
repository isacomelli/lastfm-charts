# %% [markdown]
# ### CAMADA SILVER - Limpeza e Padronização
# Lê o CSV raw da Bronze, aplica transformações e salva em Parquet em data/silver/.
# 
# Transformações aplicadas:
#   - Renomeia colunas para snake_case
#   - Remove colunas inúteis (mbid, streamable, url, @attr)
#   - Converte timestamp Unix → datetime
#   - Extrai colunas de data: day, month, month_name, year, hour, weekday, weekday_name,
#     week_of_year, quarter, semester
#   - Remove duplicatas
#   - Trata nulos
#   - Cria coluna title = track_name + ' - ' + artist_name (mantida da lógica original)
#   - Cria year_month temporariamente para os gráficos (removida antes de salvar o Parquet)
#   - Gera relatório básico de qualidade + 6 gráficos em silver_report.md

# %%
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # sem interface gráfica para ser compatível com Docker
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# %%
BRONZE_PATH = os.path.join('data', 'bronze', 'bronze.csv')
SILVER_DIR  = os.path.join('data', 'silver')
GRAPHS_DIR  = os.path.join(SILVER_DIR, 'graphs')
REPORT_PATH = os.path.join(SILVER_DIR, 'silver_report.md')

os.makedirs(SILVER_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

# %% [markdown]
# #### Leitura

# %%
print('Lendo Bronze...')
df = pd.read_csv(BRONZE_PATH, low_memory=False)
print(f'  Shape inicial: {df.shape}')

# %% [markdown]
# #### Renomear colunas para snake_case

# %%
RENAME_MAP = {
    'name'          : 'track_name'
    ,'artist.#text' : 'artist_name'
    ,'album.#text'  : 'album_name'
    ,'date.uts'     : 'timestamp_unix'
    ,'date.#text'   : 'datetime_raw'
    ,'_display_name': 'username'
}

df = df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns})

# %% [markdown]
# #### Remover colunas inúteis

# %%
DROP_PATTERNS = ['mbid', 'streamable', 'url', '@attr', 'loved', '_drop']
cols_to_drop = [c for c in df.columns if any(p in c.lower() for p in DROP_PATTERNS)]
df = df.drop(columns=cols_to_drop, errors='ignore')
print(f'  Colunas removidas: {cols_to_drop}')

# %% [markdown]
# #### Converter timestamp

# %%
df['timestamp_unix'] = pd.to_numeric(df['timestamp_unix'], errors='coerce')
df['datetime_utc']   = pd.to_datetime(df['timestamp_unix'], unit='s', utc=True)

# %% [markdown]
# #### Extrair colunas de data/tempo

# %%
df['year']         = df['datetime_utc'].dt.year
df['month']        = df['datetime_utc'].dt.month
df['month_name']   = df['datetime_utc'].dt.strftime('%B')  # January, February...
df['day']          = df['datetime_utc'].dt.day
df['hour']         = df['datetime_utc'].dt.hour
df['weekday']      = df['datetime_utc'].dt.dayofweek       # 0=Monday
df['weekday_name'] = df['datetime_utc'].dt.strftime('%A')  # Monday, Tuesday...
df['week_of_year'] = df['datetime_utc'].dt.isocalendar().week.astype(int)
df['quarter']      = df['datetime_utc'].dt.quarter
df['semester']     = df['month'].apply(lambda m: 1 if m <= 6 else 2)

# %% [markdown]
# #### Coluna title (legado do projeto original)

# %%
df['title'] = df['track_name'].fillna('') + ' - ' + df['artist_name'].fillna('')

# %% [markdown]
# #### Padronizar strings

# %%
for col in ['track_name', 'artist_name', 'album_name', 'username']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# %% [markdown]
# #### Remover duplicatas

# %%
before = len(df)
df = df.drop_duplicates(subset=['username', 'timestamp_unix'])
print(f'  Duplicatas removidas: {before - len(df)}')

# %% [markdown]
# #### Tratar nulos

# %%
null_report = df.isnull().sum()
null_report = null_report[null_report > 0]
print(f'  Nulos encontrados:\n{null_report}')

# Nulos em strings → 'Unknown'
for col in ['track_name', 'artist_name', 'album_name']:
    if col in df.columns:
        df[col] = df[col].replace('nan', 'Unknown').fillna('Unknown')

# Remove linhas sem timestamp (não há como posicioná-las no tempo) e sem username (não há como associá-las a um usuário)
df = df.dropna(subset=['timestamp_unix', 'username'])

# %% [markdown]
# #### Salvar Parquet

# %%
parquet_path = os.path.join(SILVER_DIR, 'silver.parquet')
df.to_parquet(parquet_path, index=False)
print(f'\nSilver salva em {parquet_path}')
print(f'  Shape final: {df.shape}')
print(f'  Colunas: {list(df.columns)}')

# %% [markdown]
# #### Carga da Silver no PostgreSQL

# %% 
DB_URL = (
    f'postgresql+psycopg2://'
    f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}"
    f"/{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DB_URL)

# DROP CASCADE para não quebrar views dependentes (como gold.stg_scrobbles)
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS silver.scrobbles CASCADE'))
    conn.commit()

df.to_sql(
    'scrobbles'
    ,engine
    ,schema='silver'
    ,if_exists='append'
    ,index=False
    ,method='multi'
    ,chunksize=10000
)
print(f'{len(df):,} linhas carregadas em silver.scrobbles')

# %% [markdown]
# #### Gráficos

# %%
STYLE = {
    'figure.facecolor': '#0d1117'
    ,'axes.facecolor' : '#161b22'
    ,'axes.edgecolor' : '#30363d'
    ,'axes.labelcolor': 'white'
    ,'xtick.color'    : 'white'
    ,'ytick.color'    : 'white'
    ,'text.color'     : 'white'
    ,'grid.color'     : '#21262d'
}
plt.rcParams.update(STYLE)
ACCENT = '#1db954'  # verde spotify

graph_paths = []

## G1 - Scrobbles por usuário
fig, ax = plt.subplots(figsize=(8, 4))
counts = df.groupby('username').size().sort_values(ascending=False)
ax.bar(counts.index, counts.values, color=ACCENT)
ax.set_title('Scrobbles por Usuário', fontsize=14, pad=12)
ax.set_xlabel('Usuário')
ax.set_ylabel('Scrobbles')
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.set_xticks(range(len(counts)))
ax.set_xticklabels(counts.index, rotation=45, ha='right')
plt.tight_layout()
p = os.path.join(GRAPHS_DIR, 'g1_scrobbles_por_usuario.png')
plt.savefig(p, dpi=120)
plt.close()
graph_paths.append(p)

## G2 - Top 10 artistas do grupo
fig, ax = plt.subplots(figsize=(9, 5))
top_artists = df.groupby('artist_name').size().sort_values(ascending=False).head(10)
ax.barh(top_artists.index[::-1], top_artists.values[::-1], color=ACCENT)
ax.set_title('Top 10 Artistas do Grupo', fontsize=14, pad=12)
ax.set_xlabel('Scrobbles')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
p = os.path.join(GRAPHS_DIR, 'g2_top10_artistas.png')
plt.savefig(p, dpi=120)
plt.close()
graph_paths.append(p)

## G3 - Distribuição de scrobbles por hora do dia
fig, ax = plt.subplots(figsize=(10, 4))
hour_counts = df.groupby('hour').size()
ax.bar(hour_counts.index, hour_counts.values, color=ACCENT)
ax.set_title('Distribuição de Scrobbles por Hora do Dia', fontsize=14, pad=12)
ax.set_xlabel('Hora')
ax.set_ylabel('Scrobbles')
ax.set_xticks(range(0, 24))
plt.tight_layout()
p = os.path.join(GRAPHS_DIR, 'g3_hora_do_dia.png')
plt.savefig(p, dpi=120)
plt.close()
graph_paths.append(p)

## G4 - Scrobbles por dia da semana
fig, ax = plt.subplots(figsize=(8, 4))
day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
day_counts = df.groupby('weekday_name').size().reindex(day_order, fill_value=0)
ax.bar(day_counts.index, day_counts.values, color=ACCENT)
ax.set_title('Scrobbles por Dia da Semana', fontsize=14, pad=12)
ax.set_xlabel('Dia')
ax.set_ylabel('Scrobbles')
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
p = os.path.join(GRAPHS_DIR, 'g4_dia_da_semana.png')
plt.savefig(p, dpi=120)
plt.close()
graph_paths.append(p)

## G5 - Evolução mensal de scrobbles (todos os usuários)
fig, ax = plt.subplots(figsize=(12, 4))
df['year_month'] = df['datetime_utc'].dt.to_period('M')
monthly = df.groupby('year_month').size()
ax.plot(monthly.index.astype(str), monthly.values, color=ACCENT, linewidth=1.5)
ax.fill_between(range(len(monthly)), monthly.values, alpha=0.15, color=ACCENT)
ax.set_title('Evolução Mensal de Scrobbles', fontsize=14, pad=12)
ax.set_xlabel('Mês/Ano')
ax.set_ylabel('Scrobbles')
step = max(1, len(monthly) // 12)
ax.set_xticks(range(0, len(monthly), step))
ax.set_xticklabels(monthly.index.astype(str)[::step], rotation=45, ha='right')
plt.tight_layout()
p = os.path.join(GRAPHS_DIR, 'g5_evolucao_mensal.png')
plt.savefig(p, dpi=120)
plt.close()
graph_paths.append(p)

## G6 - Boxplot de scrobbles por usuário (detecção de outliers)
fig, ax = plt.subplots(figsize=(10, 5))
user_order = df.groupby('username').size().sort_values(ascending=False).index.tolist()
box_data = [df[df['username'] == u].groupby('year_month').size().values for u in user_order]
bp = ax.boxplot(box_data, patch_artist=True, vert=True, medianprops=dict(color='white', linewidth=2))
for patch in bp['boxes']:
    patch.set_facecolor(ACCENT)
    patch.set_alpha(0.7)
for element in ['whiskers', 'caps', 'fliers']:
    for item in bp[element]:
        item.set_color('#888888')
ax.set_xticklabels(user_order, rotation=45, ha='right')
ax.set_title('Distribuição Mensal de Scrobbles por Usuário (Outliers)', fontsize=14, pad=12)
ax.set_xlabel('Usuário')
ax.set_ylabel('Scrobbles por mês')
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
p = os.path.join(GRAPHS_DIR, 'g6_outliers_por_usuario.png')
plt.savefig(p, dpi=120)
plt.close()
graph_paths.append(p)

# %% [markdown]
# Remove colunas temporárias usadas para os gráficos
df = df.drop(columns=['year_month'], errors='ignore')

# %% [markdown]
# #### Relatório Markdown

# %%
with open(REPORT_PATH, 'w', encoding='utf-8') as md:
    md.write('# Silver Layer - Relatório de Qualidade de Dados\n\n')
    md.write(f"**Data de geração:** {(pd.Timestamp.now(tz='America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M')}\n\n")
    md.write(f'**Total de registros:** {len(df):,}\n\n')
    md.write(f"**Período coberto:** {df['datetime_utc'].min()} → {df['datetime_utc'].max()}\n\n")

    md.write('## Tipos de Colunas\n\n')
    md.write('| Coluna | Tipo |\n|---|---|\n')
    for col, dtype in df.dtypes.items():
        md.write(f'| {col} | {dtype} |\n')

    md.write('\n## Valores Nulos\n\n')
    if null_report.empty:
        md.write('Nenhum valor nulo encontrado após tratamento.\n\n')
    else:
        md.write('| Coluna | Nulos |\n|---|---|\n')
        for col, n in null_report.items():
            pct = n / len(df) * 100
            md.write(f'| {col} | {n:,} ({pct:.1f}%) |\n')

    md.write('\n## Estatísticas Descritivas\n\n')
    md.write(df[['hour', 'weekday', 'month', 'year']].describe().to_markdown())

    md.write('\n\n## Gráficos\n\n')
    for path in graph_paths:
        fname = os.path.basename(path)
        md.write(f'![{fname}](graphs/{fname})\n\n')

print(f'Relatório salvo em {REPORT_PATH}')