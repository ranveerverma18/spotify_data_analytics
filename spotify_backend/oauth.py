import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = 'e406584407bc4d6abfbc0ed5052983e0'
CLIENT_SECRET = '3052c144d4d1423e9b9bcdf02d587cc5'
REDIRECT_URI = 'http://127.0.0.1:8000/callback'

SCOPE = "user-read-private user-read-email user-top-read user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative"

def authenticate_spotify():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))
    return sp

def fetch_user_data(access_token):
    # Fetch basic user profile data using requests
    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch user data: {response.status_code}")

    # Debugging: print the raw response content to understand its format
    print("Raw response from Spotify API:", response.text)

    user_data = response.json()

    # Now use spotipy to fetch additional data (like top tracks, top artists, etc.)
    sp = authenticate_spotify()

    try:
        # Fetch additional details with spotipy
        top_tracks = sp.current_user_top_tracks(limit=10)
        top_artists = sp.current_user_top_artists(limit=10)
        liked_songs = sp.current_user_saved_tracks(limit=10)
        recently_played = sp.current_user_recently_played(limit=10)
        playlists = sp.current_user_playlists(limit=10)

        # Combine both the API and spotipy data
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

# Example usage of the function:
access_token = "your_access_token_here"
user_data = fetch_user_data(access_token)
print(user_data)


        

