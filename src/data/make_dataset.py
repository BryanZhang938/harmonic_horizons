import base64
import os
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from dotenv import load_dotenv
from requests import get, post

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')


def get_token() -> str:
    """
    Retrieves an access token from the Spotify API.

    @return: The access token as a string.
    @rtype: str
    """
    auth_string = f'{client_id}:{client_secret}'
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    call_headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers=call_headers, data=data)
    result.raise_for_status()
    token = result.json()['access_token']

    return token


auth_token = get_token()
headers = {'Authorization': f'Bearer {auth_token}'}


def search_for(search_query: str, *filters: str, limit: int = 10) -> dict:
    """
    Searches Spotify for the given query and filters. It returns the JSON response as a dictionary.

    @rtype: dict
    @param search_query: The query string to search for.
    @param filters: The types of items to search for (e.g., 'artist', 'album', 'track').
    @param limit: The maximum number of results to return (default is 10).
    @return: The JSON response of results as a dictionary.
    """
    query_url = f'https://api.spotify.com/v1/search?q={search_query}&type={','.join(filters)}&limit={limit}'
    result = get(query_url, headers=headers)
    result.raise_for_status()

    return result.json()


def get_playlist_tracks(playlist_id: str) -> dict:
    """
    Retrieves the tracks of a given playlist. It returns the JSON response as a dictionary.

    @param playlist_id: The ID of the playlist to retrieve tracks from.
    @type playlist_id: str

    @return: The JSON response containing the playlist tracks as a dictionary.
    @rtype: dict
    """
    query_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    result = get(query_url, headers=headers)
    result.raise_for_status()

    return result.json()


def get_track_features(track_ids: list) -> dict:
    """
    Retrieves audio features for a list of track IDs. It returns the JSON response as a dictionary.

    @param track_ids: A list of track IDs to retrieve audio features for.
    @type track_ids: list

    @return: The JSON response containing the audio features as a dictionary.
    @rtype: dict
    """
    query_url = f'https://api.spotify.com/v1/audio-features/'
    result = get(query_url, headers=headers, params={'ids': ','.join(track_ids)})
    result.raise_for_status()

    return result.json()


def get_track_info(track_ids: list) -> dict:
    """
    Retrieves detailed information of a track for a list of track IDs. The JSON response is returned as a dictionary.

    @param track_ids: A list of track IDs to retrieve detailed information for.
    @type track_ids: list

    @return: The JSON response containing the track information as a dictionary.
    @rtype: dict
    """
    query_url = f'https://api.spotify.com/v1/tracks'
    result = get(query_url, headers=headers, params={'ids': ','.join(track_ids)})
    result.raise_for_status()

    return result.json()


def get_playlist_ids(keyword: str) -> list:
    """
    Retrieves a list of playlist IDs based on a search query. It returns a list of playlist IDs from the search results.

    @param keyword: The keyword to search for playlists.
    @type keyword: str

    @return: A list of playlist IDs.
    @rtype: list
    """
    search = search_for(keyword, 'playlist', limit=7)
    return [item['id'] for item in search['playlists']['items']]


def get_track_ids(playlist_id: str) -> list:
    """
    Retrieves a list of track IDs from a given playlist. It returns a list of track IDs from the playlist.

    @param playlist_id: The ID of the playlist to retrieve track IDs from.
    @type playlist_id: str

    @return: A list of track IDs.
    @rtype: list
    """
    tracks = get_playlist_tracks(playlist_id)['items']
    return [track_id['track']['id'] for track_id in tracks if track_id['track'] and track_id['track']['id'] is not None]


def extract_features(tracks: list) -> list:
    """
    Recursively retrieves audio features for a list of track IDs from the Spotify API. It returns a list of audio
    features for all the tracks.

    @param tracks: A list of track IDs to retrieve audio features for.
    @type tracks: list

    @return: A list of audio features for the specified track IDs.
    @rtype: list
    """
    if len(tracks) == 0:
        return []

    return get_track_features(tracks[:100])['audio_features'] + extract_features(tracks[100:])


def extract_info(tracks: list) -> list:
    """
    Recursively retrieves detailed information for a list of track IDs. It returns a list of dictionaries containing
    the track name, popularity, and ID for all the tracks.

    @param tracks: A list of track IDs to retrieve detailed information for.
    @type tracks: list

    @return: A list of dictionaries with track information (name, popularity, and ID).
    @rtype: list
    """
    if len(tracks) == 0:
        return []

    track_info = get_track_info(tracks[:50])['tracks']
    extracted_info = [{'name': info['name'], 'popularity': info['popularity'], 'id': info['id']}
                      if info else {'name': None, 'popularity': None, 'id': None} for info in track_info]

    return extracted_info + extract_info(tracks[50:])


mood_keywords = {
    "happy": [
        "feel good songs",
        "upbeat party anthems",
        "happy summer hits",
        "cheerful pop tracks",
        "joyful dance songs",
        "energetic sing-along tunes"
    ],
    "sad": [
        "melancholic ballads",
        "heartbreak songs",
        "sad rainy day playlist",
        "emotional slow songs",
        "depressing acoustic songs"
    ],
    "angry": [
        "angry rock anthems",
        "rage metal tracks",
        "intense workout songs",
        "aggressive punk music",
        "fierce rap battle songs"
    ],
    "calm": [
        "relaxing acoustic vibes",
        "chill lo-fi beats",
        "peaceful ambient music",
        "calm meditation tracks"
    ]
}


playlist_ids = []
used_track_ids = set()
df_tracks = []

with ThreadPoolExecutor() as executor:
    for mood, keyword in mood_keywords.items():
        playlist_results = executor.map(get_playlist_ids, keyword)
        for playlist_result in playlist_results:
            playlist_ids.extend([(playlist_id, mood) for playlist_id in playlist_result])

with ThreadPoolExecutor() as executor:
    for playlist_id, mood in playlist_ids:
        track_ids = get_track_ids(playlist_id)
        unique_track_ids = [track_id for track_id in track_ids if track_id not in used_track_ids]

        df_tracks.extend([(track_id, mood) for track_id in unique_track_ids])
        used_track_ids.update(unique_track_ids)

track_ids, moods = zip(*df_tracks) if df_tracks else ([], [])

track_data = extract_features(track_ids)
track_infos = extract_info(track_ids)

track_data = [track for track in track_data if track is not None]
track_infos = [info for info in track_infos if info is not None]

track_df = pd.DataFrame(track_data)
track_info_df = pd.DataFrame(track_infos)
track_info_df['mood'] = moods

merged_track_df = track_df.merge(track_info_df, on='id')

merged_track_df.to_csv('/Users/bryanzhang/Desktop/career/projects/harmonic_horizons/data/tracks.csv')
