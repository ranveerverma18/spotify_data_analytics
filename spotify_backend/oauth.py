from spotipy.oauth2 import SpotifyOAuth
import spotipy

CLIENT_ID = 'e406584407bc4d6abfbc0ed5052983e0'
CLIENT_SECRET = '3052c144d4d1423e9b9bcdf02d587cc5'
REDIRECT_URI = 'http://127.0.0.1:8000/callback'

SCOPE = "user-read-private user-read-email user-top-read user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative"

def get_spotify_auth_url():
    auth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    return auth.get_authorize_url()

def get_tokens(code):
    auth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    token_info = auth.get_access_token(code)
    return token_info['access_token']  # 👈 return just the access token


def fetch_user_data(access_token):
    sp = spotipy.Spotify(auth=access_token)

    try:
        user_data = {
            "user_profile": sp.current_user(),
            "top_tracks": sp.current_user_top_tracks(limit=10),
            "top_artists": sp.current_user_top_artists(limit=10),
            "liked_songs": sp.current_user_saved_tracks(limit=10),
            "recently_played": sp.current_user_recently_played(limit=10),
            "playlists": sp.current_user_playlists(limit=10)
        }
        return user_data

    except spotipy.exceptions.SpotifyException as e:
        print(f"Spotify API error: {e}")
        raise
        

