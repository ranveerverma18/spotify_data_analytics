from spotipy.oauth2 import SpotifyOAuth
import spotipy

CLIENT_ID = 'e406584407bc4d6abfbc0ed5052983e0'
CLIENT_SECRET = '3052c144d4d1423e9b9bcdf02d587cc5'
REDIRECT_URI = 'http://localhost:8000/callback'

SCOPE = "user-read-private user-read-email user-top-read user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative"

def get_spotify_auth_url():
    auth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    return auth.get_authorize_url()

def get_tokens(code):
    auth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    token_info = auth.get_access_token(code)
    return token_info

def fetch_user_data(access_token):
    sp = spotipy.Spotify(auth=access_token)

    user_data = {
        "user_profile": sp.current_user(),
        "top_tracks": sp.current_user_top_tracks(limit=10),
        "top_artists": sp.current_user_top_artists(limit=10),
        "liked_songs": sp.current_user_saved_tracks(limit=10),
        "recently_played": sp.current_user_recently_played(limit=10),
        "playlists": sp.current_user_playlists(limit=10)
    }

    return user_data

