import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import pandas as pd
import os
import joblib

load_dotenv()

# Authenticate Spotify API
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri='http://localhost:8888/callback',
                                               scope='user-top-read'))

# Get user's most listened to tracks.
results = sp.current_user_top_tracks(limit=50, time_range='medium_term')
top_tracks = results['items']

# Recommendation Algorithm
seed_tracks = [track['id'] for track in top_tracks[:5]]
recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=100)
recommended_tracks = recommendations['tracks']

track_names = [track['name'] for track in recommended_tracks]
track_ids = [track['id'] for track in recommended_tracks]
track_popularity = [track['popularity'] for track in recommended_tracks]
audio_features = sp.audio_features(track_ids)

# Add recommended tracks into DataFrame
track_data = []
for i, feature in enumerate(audio_features):
    if feature:
        track_info = {
            'name': track_names[i],
            'danceability': feature['danceability'],
            'energy': feature['energy'],
            'key': feature['key'],
            'loudness': feature['loudness'],
            'mode': feature['mode'],
            'speechiness': feature['speechiness'],
            'acousticness': feature['acousticness'],
            'instrumentalness': feature['instrumentalness'],
            'liveness': feature['liveness'],
            'valence': feature['valence'],
            'tempo': feature['tempo'],
            'duration_s': feature['duration_ms'] / 1000,
            'time_signature': feature['time_signature'],
            'popularity': track_popularity[i]
        }
        track_data.append(track_info)

df = pd.DataFrame(track_data)

# Predict Mood
directory = '/harmonic_horizons/src/models'

loaded_knn = joblib.load(os.path.join(directory, 'best_knn_model.pkl'))
loaded_scaler = joblib.load(os.path.join(directory, 'scaler.pkl'))

X = df.drop(columns=['key', 'time_signature', 'liveness', 'tempo', 'name'])
X_scaled = loaded_scaler.transform(X)
prediction = loaded_knn.predict(X_scaled)

df['mood'] = prediction
moods = ', '.join(df['mood'].unique())

# User Input
user_mood = input(f"Enter your mood ({moods}): ")
recommended_mood_tracks = df[df['mood'] == user_mood]

print('Recommended Tracks:')
for i, track in enumerate(recommended_mood_tracks['name']):
    print(f"{i+1}. {track}")
