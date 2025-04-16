import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = 'e406584407bc4d6abfbc0ed5052983e0'
CLIENT_SECRET = '3052c144d4d1423e9b9bcdf02d587cc5'
REDIRECT_URI = 'http://127.0.0.1:8000/callback'

SCOPE = "user-read-private user-read-email user-top-read user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative"

def get_spotify_auth_url():
    """Generate the Spotify authentication URL"""
    auth_url = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ).get_authorize_url()
    return auth_url

def authenticate_spotify():
    """Authenticate the user and get the spotipy instance"""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))
    return sp

def fetch_user_data(access_token):
    """Fetch user data using the provided access token"""
    sp = spotipy.Spotify(auth=access_token)

    try:
        # Fetch basic user profile data using spotipy
        user_data = sp.current_user()

        # Fetch additional data like top tracks, top artists, etc.
        top_tracks = sp.current_user_top_tracks(limit=10)
        top_artists = sp.current_user_top_artists(limit=10)
        liked_songs = sp.current_user_saved_tracks(limit=10)
        recently_played = sp.current_user_recently_played(limit=10)
        playlists = sp.current_user_playlists(limit=10)

        # Combine the data into a single dictionary
        full_user_data = {
            "user_profile": user_data,
            "top_tracks": top_tracks,
            "top_artists": top_artists,
            "liked_songs": liked_songs,
            "recently_played": recently_played,
            "playlists": playlists
        }

        return full_user_data

    except spotipy.exceptions.SpotifyException as e:
        print(f"Spotify API error: {e}")
        raise



        

