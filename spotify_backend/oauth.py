import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.responses import RedirectResponse
from typing import Optional
import logging
from base64 import b64encode
from urllib.parse import urlencode
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace these with your actual Spotify Developer credentials.  Do NOT hardcode in a production environment.  Use environment variables.
SPOTIFY_CLIENT_ID = os.getenv("e406584407bc4d6abfbc0ed5052983e0")
SPOTIFY_CLIENT_SECRET = os.getenv("3052c144d4d1423e9b9bcdf02d587cc5")
SPOTIFY_REDIRECT_URI = "http://localhost:8000/callback"
# SPOTIFY_REDIRECT_URI = "http://localhost:8000/callback" #  You had this.  Be consistent.
SCOPE = (
    "user-read-private user-read-email user-top-read "
    "user-library-read user-read-recently-played "
    "playlist-read-private playlist-read-collaborative"
)
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"  # Correct Spotify token URL

app = FastAPI()

def get_spotify_oauth():
    """
    Create and return a SpotifyOAuth object.  This is a dependency.
    """
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True, # Add this to force showing the dialog
    )
    

# Function to get the authorization URL
@app.get("/login")
def login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)

# Function to exchange authorization code for access and refresh tokens
@app.get("/callback")
def callback(request: Request, code: str = None):
    """
    Endpoint to handle the Spotify callback and exchange the authorization code for tokens.
    """
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_access_token(code)
    # Here, you should store token_info in a session or issue a JWT
    # For demo, redirect to frontend with a dummy token
    frontend_url = f"http://localhost:5173/dashboard?token={token_info['access_token']}"
    return RedirectResponse(frontend_url)

# Function to authenticate user via Spotipy (using a dependency)
def get_spotify_client(token_info: dict):
    """
    Create a Spotipy client from a token_info dictionary.
    """
    return spotipy.Spotify(auth=token_info['access_token'])


# Function to fetch extended user data
@app.get("/me")
async def get_me(token: str = Query(...)):
    """
    Endpoint to fetch user data.
    """
    try:
        sp = spotipy.Spotify(auth=token)
        return sp.current_user()
    except spotipy.SpotifyException as e:
        raise HTTPException(status_code=e.http_status, detail=e.msg)
    except Exception as e:
        logging.error(f"Error fetching user data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user data")
    
@app.get("/user_data")
async def get_user_data(token: str = Query(...)):
    """
    Endpoint to fetch extended user data using the provided access token.
    """
    try:
        sp = spotipy.Spotify(auth=token)

        user_data = sp.current_user()
        top_tracks = sp.current_user_top_tracks(limit=10)
        top_artists = sp.current_user_top_artists(limit=10)
        liked_songs = sp.current_user_saved_tracks(limit=10)
        recently_played = sp.current_user_recently_played(limit=10)
        playlists = sp.current_user_playlists(limit=10)

        return {
            "user_profile": user_data,
            "top_tracks": top_tracks,
            "top_artists": top_artists,
            "liked_songs": liked_songs,
            "recently_played": recently_played,
            "playlists": playlists,
        }

    except spotipy.SpotifyException as e:
        logging.error(f"Spotify API error: {e}")
        raise HTTPException(status_code=e.http_status, detail=e.msg)
    except Exception as e:
        logging.error(f"Error fetching user data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user data from Spotify")
        

if __name__ == "__main__":
    import uvicorn
    #  Use the standard FastAPI way to run the app.
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)








        

