import base64
import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from dotenv import load_dotenv
from requests import get, post

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

def get_token():
    try:
        auth_string = f'{client_id}:{client_secret}'
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

        url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}
        result = post(url, headers=headers, data=data)
        result.raise_for_status()
        token = result.json()['access_token']

        return token
    except:
        return None

token = get_token()
headers = {'Authorization': f'Bearer {token}'}

def search_for(search_query, *filters, limit = 10):
    query_url = f'https://api.spotify.com/v1/search?q={search_query}&type={','.join(filters)}&limit={limit}'
    result = get(query_url, headers=headers)
    result.raise_for_status()

    return result.json()

def get_playlist_tracks(playlist_id):
    query_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    result = get(query_url, headers=headers)
    result.raise_for_status()

    return result.json()

def get_track_features(track_ids):
    query_url = f'https://api.spotify.com/v1/audio-features/'
    result = get(query_url, headers=headers, params={'ids': ','.join(track_ids)})
    result.raise_for_status

    return result.json()

def get_playlist_ids(keyword):
    search = search_for(keyword, 'playlist', limit=2)
    return [item['id'] for item in search['playlists']['items']]

def get_track_ids(playlist_id):
    tracks = get_playlist_tracks(playlist_id)['items']
    return [track['track']['id'] for track in tracks]

def extract_all(tracks):
    if len(tracks) == 0:
        return []
    
    return get_track_features(tracks[:100])['audio_features'] + extract_all(tracks[100:])

keywords = [
    "greatest hits",
    "top 100",
    "best songs ever",
    "all-time favorites",
    "most streamed songs",
    "classic hits",
    "legendary tracks",
    "iconic songs",
    "chart-toppers",
    "record breakers",
    "masterpieces",
    "famous songs"
]

playlist_ids = set()
track_ids = set()

with ThreadPoolExecutor() as executor:
    playlist_results = executor.map(get_playlist_ids, keywords)
    for playlist_result in playlist_results:
        playlist_ids.update(playlist_result)
    
    track_results = executor.map(get_track_ids, playlist_ids)
    for track_result in track_results:
        track_ids.update(track_result)

track_ids = list(track_ids)
track_data = extract_all(track_ids)
track_df = pd.DataFrame(track_data)

track_df.to_csv('top_tracks.csv')