import logging
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING # Import DESCENDING

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spotify API Credentials (Temporary hardcoded values)
SPOTIPY_CLIENT_ID = "e406584407bc4d6abfbc0ed5052983e0"
SPOTIPY_CLIENT_SECRET = "3052c144d4d1423e9b9bcdf02d587cc5"
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8000/callback"
SPOTIPY_SCOPE = (
    "user-read-private user-read-email user-top-read user-library-read "
    "user-read-recently-played playlist-read-private playlist-read-collaborative"
)

# MongoDB Connection
MONGO_URI = "mongodb+srv://ranveerverma18:ranveer18@mongo-db-cluster.7xghnej.mongodb.net/?retryWrites=true&w=majority&appName=mongo-db-cluster"

# MongoDB Connection
def get_database():
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        logging.info("MongoDB connection successful!")
        return client.spotify_data # Database name is spotify_data
    except Exception as e:
        logging.error(f"MongoDB connection error: {e}")
        raise HTTPException(status_code=500, detail="Could not connect to MongoDB")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SpotifyOAuth object
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SPOTIPY_SCOPE,
    show_dialog=True
)

@app.get("/auth/spotify")
async def login():
    """
    Endpoint to initiate the Spotify authorization flow.
    Redirects the user to Spotify's authorization page.
    """
    try:
        auth_url = sp_oauth.get_authorize_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logging.error(f"Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate authorization URL")

@app.get("/callback")
async def callback(code: str = Query(None)):
    """
    Endpoint to handle the Spotify callback and exchange the authorization code for tokens.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    try:
        token_info = sp_oauth.get_access_token(code)
        if not token_info:
            raise HTTPException(status_code=400, detail="Failed to get access token from Spotify")

        # In a real application, you would store these tokens securely associated with a user
        access_token = token_info["access_token"]
        refresh_token = token_info.get("refresh_token")

        # Redirect to frontend with tokens
        frontend_url = "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/dashboard?access_token={access_token}&refresh_token={refresh_token}"
        )

    except Exception as e:
        logging.error(f"Error during token exchange: {e}")
        raise HTTPException(status_code=500, detail="Error during token exchange")

@app.get("/refresh_token")
async def refresh_token(refresh_token: str = Query(...)):
    """
    Endpoint to refresh an expired access token.
    """
    try:
        token_info = sp_oauth.refresh_access_token(refresh_token)
        if not token_info:
            raise HTTPException(status_code=400, detail="Failed to refresh access token")

        return {
            "access_token": token_info["access_token"],
            "refresh_token": token_info.get("refresh_token", refresh_token)
        }
    except Exception as e:
        logging.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail="Error refreshing token")

@app.get("/user/data")
async def get_user_data(access_token: str = Query(...), db: MongoClient = Depends(get_database)):
    """
    Endpoint to fetch user-specific data from MongoDB.
    """
    try:
        # Use the access token to get the Spotify user ID
        sp = spotipy.Spotify(auth=access_token)
        user = sp.me()
        spotify_user_id = user["id"]
        logging.info(f"Fetching data for user: {spotify_user_id}")

        # List of collections to fetch data from
        collections_to_fetch = [
            'spotify_liked_songs',
            'spotify_recently_played',
            'spotify_top_artists',
            'spotify_top_tracks',
            'spotify_user_playlists',
            'spotify_user_profile',
        ]

        user_data = {}
        fetch_limit = 500 # Limit the number of documents fetched per collection

        # Fetch data from each collection with sorting and limiting
        for collection_name in collections_to_fetch:
            collection = db[collection_name]
            # Query for documents matching the user_id, sort by _id descending, and limit
            data_from_collection = list(collection.find({"user_id": spotify_user_id}).sort('_id', DESCENDING).limit(fetch_limit))

            # Convert ObjectId to string for JSON serialization
            for item in data_from_collection:
                item["_id"] = str(item["_id"])

            user_data[collection_name] = data_from_collection

        return user_data

    except Exception as e:
        logging.error(f"Error fetching user data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user data")

@app.get("/test_token")
async def test_token(access_token: str = Query(...)):
    """
    Endpoint to test if a given access token is valid by fetching basic user info.
    **This is for testing purposes only and should be removed in production.**
    """
    try:
        sp = spotipy.Spotify(auth=access_token)
        user = sp.me()
        return {"user_id": user["id"], "display_name": user.get("display_name")}
    except Exception as e:
        logging.error(f"Error using access token: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")










        

