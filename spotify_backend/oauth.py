import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import HTTPException
import logging

# Replace with your credentials
SPOTIFY_CLIENT_ID = "your_spotify_client_id"
SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/callback"

SCOPE = "user-read-private user-read-email user-top-read user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative"

# Function to get the authorization URL
def get_spotify_auth_url():
    """Generate the Spotify authentication URL"""
    auth_url = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE
    ).get_authorize_url()
    return auth_url

# Function to exchange authorization code for access token
def get_tokens(code: str):
    """Exchange the authorization code for access and refresh tokens using requests"""
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"  # Base64 encoded
    }
    data = {
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        tokens = response.json()  # Make sure the response is a dictionary
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        return access_token, refresh_token
    else:
        logging.error(f"Error fetching tokens: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to get access token")

def authenticate_spotify():
    """Authenticate the user and get the spotipy instance"""
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
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
        logging.error(f"Spotify API error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user data from Spotify")





        

