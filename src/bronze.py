# %% [markdown]
# ### Camada Bronze: Ingestão Raw
# Coleta os scrobbles de cada usuário via Last.fm API e salva em data/bronze/ sem alterações.

# %%
import os
import time
import json
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# %%
API_KEY  = os.getenv('LASTFM_API_KEY')
BASE_URL = 'https://ws.audioscrobbler.com/2.0/'

# Usuários do grupo
USERNAMES = {
    'Tais'            : 'taizzzx' # Segunda usuária menos ativa
    ,'Isa'              : 'isacomelli_'
    ,'Mari'            : 'bluesandrugs'
    ,'Nico'            : 'nicolacioo'
    ,'Ruds'            : 'henryhudson20'
    ,'Sarinha'         : 'sarasicsu'
    ,'Joao'            : 'jopefroes'
    ,'Gustavo'         : 'e_o_pivas'
    ,'Lucas I'         : 'lucasntss'
    ,'Dora'            : 'doraaraujo_' # Usuária menos ativa
    ,'Sarah'           : 'aquariaty'
    ,'Brasao'          : 'Brasaum'
    ,'Lucas N'         : 'lucasraikou'
    ,'Davi'            : 'davizooca'
}

# Coleta desde o início do Last.fm
FROM_TIMESTAMP = int(datetime.strptime('2004-01-01', '%Y-%m-%d').timestamp())

BRONZE_DIR      = os.path.join('data', 'bronze')
CHECKPOINT_PATH = os.path.join('data', 'bronze', 'checkpoint.json')
os.makedirs(BRONZE_DIR, exist_ok=True)

# %%
def load_checkpoint() -> dict:
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH, 'r') as f:
            return json.load(f)
    return {}


def save_checkpoint(checkpoint: dict):
    with open(CHECKPOINT_PATH, 'w') as f:
        json.dump(checkpoint, f, indent=2)


def get_recent_tracks(username: str, page: int = 1, limit: int = 200, retries: int = 3, from_timestamp: int = None) -> dict:
    params = {
        'method'  : 'user.getrecenttracks'
        ,'user'   : username
        ,'api_key': API_KEY
        ,'format' : 'json'
        ,'limit'  : limit
        ,'page'   : page
        ,'from'   : from_timestamp if from_timestamp else FROM_TIMESTAMP
    }

    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code >= 500:
                wait = 5 * (attempt + 1)
                print(f'  Erro {response.status_code} na página {page}, tentativa {attempt + 1}/{retries}. Aguardando {wait}s...')
                time.sleep(wait)
            else:
                raise e

    raise Exception(f'Falhou após {retries} tentativas na página {page}')


def collect_user_tracks(display_name: str, username: str, checkpoint: dict, from_timestamp: int = None) -> list[dict]:
    # se veio from_timestamp, começa do zero (é uma coleta incremental)
    if from_timestamp:
        all_tracks = []
        start_page = 1
    else:
        all_tracks = checkpoint.get(username, {}).get('tracks', [])
        start_page = checkpoint.get(username, {}).get('last_page', 0) + 1

    _from = (from_timestamp if from_timestamp else FROM_TIMESTAMP)

    page = start_page

    while True:
        data = get_recent_tracks(username, page=page, from_timestamp=_from)
        tracks = [
            t for t in data['recenttracks']['track']
            if not t.get('@attr', {}).get('nowplaying')
        ]
        total_pages = int(data['recenttracks']['@attr']['totalPages'])

        all_tracks.extend(tracks)
        print(f'  [{display_name}] página {page}/{total_pages} - {len(all_tracks)} scrobbles coletados')

        # salva checkpoint a cada página
        checkpoint[username] = {
            'last_page'   : page
            ,'total_pages': total_pages
            ,'tracks'     : all_tracks
        }
        save_checkpoint(checkpoint)

        if page >= total_pages:
            break

        page += 1
        # time.sleep(0.1)

    return all_tracks

def main():
    checkpoint = load_checkpoint()
    all_bronze = []

    for display_name, username in USERNAMES.items():
        user_path = os.path.join(BRONZE_DIR, f'{username}_bronze.json')
        print(f'  Procurando: {user_path} — existe: {os.path.exists(user_path)}')

        # atualiza o bronze se já tiver um arquivo, coletando só o que é novo desde o último timestamp
        if os.path.exists(user_path):
            with open(user_path, 'r', encoding='utf-8') as f:
                existing_tracks = json.load(f)
            
            # garante _display_name em todos os tracks existentes
            for t in existing_tracks:
                t['_display_name'] = display_name
            
            # pega o scrobble mais recente
            last_timestamp = max(int(t['date']['uts']) for t in existing_tracks if 'date' in t)
            last_date = datetime.fromtimestamp(last_timestamp).strftime('%d/%m/%Y %H:%M:%S')
            print(f'  [{display_name}] JSON existe, coletando apenas novos scrobbles a partir de {last_date}...')
            
            new_tracks = collect_user_tracks(display_name, username, checkpoint, from_timestamp=last_timestamp + 1)
            
            if new_tracks:
                all_tracks = existing_tracks + new_tracks

                for t in new_tracks:
                    t['_display_name'] = display_name

                with open(user_path, 'w', encoding='utf-8') as f:
                    json.dump(all_tracks, f, ensure_ascii=False, indent=2)
                print(f'  {len(new_tracks)} novos scrobbles adicionados')
                
            else:
                all_tracks = existing_tracks
                print(f'  Nenhum scrobble novo')

            all_bronze.extend(all_tracks)
            continue

        # pula se já completo no checkpoint
        if (checkpoint.get(username, {}).get('last_page') == checkpoint.get(username, {}).get('total_pages')
            and checkpoint.get(username, {}).get('total_pages') is not None):
            print(f'  [{display_name}] já coletado no checkpoint, pulando...')
            all_bronze.extend(checkpoint[username]['tracks'])
            continue

        print(f'\n  Coletando: {display_name} (@{username})')
        try:
            tracks = collect_user_tracks(display_name, username, checkpoint)
            for t in tracks:
                t['_display_name'] = display_name
            all_bronze.extend(tracks)

            with open(user_path, 'w', encoding='utf-8') as f:
                json.dump(tracks, f, ensure_ascii=False, indent=2)

            print(f'  {len(tracks)} scrobbles salvos em {username}_bronze.json')

        except Exception as e:
            print(f'  Erro ao coletar {display_name}: {e}')
            print(f'  Progresso salvo no checkpoint, rode novamente para continuar.')

    if all_bronze:
        df_bronze = pd.json_normalize(all_bronze)
        consolidated_path = os.path.join(BRONZE_DIR, 'bronze.csv')
        df_bronze.to_csv(consolidated_path, index=False, encoding='utf-8')
        print(f'\n  Consolidado salvo em {consolidated_path}')
        print(f'  Total de linhas: {len(df_bronze):,}')
        print(f'  Colunas brutas: {list(df_bronze.columns)}')


if __name__ == '__main__':
    main()