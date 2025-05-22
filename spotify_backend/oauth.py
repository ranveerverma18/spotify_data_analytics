import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from spotipy.oauth2 import SpotifyOAuth

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spotify API Credentials (HARDCODED - USE WITH CAUTION)
SPOTIPY_CLIENT_ID = "e406584407bc4d6abfbc0ed5052983e0"  # REPLACE WITH YOUR CLIENT ID
SPOTIPY_CLIENT_SECRET = "3052c144d4d1423e9b9bcdf02d587cc5"  # REPLACE WITH YOUR CLIENT SECRET
SPOTIPY_REDIRECT_URI = "http://localhost:8000/callback"
SPOTIPY_SCOPE = (
    "user-read-private user-read-email user-top-read user-library-read user-read-recently-played playlist-read-private playlist-read-collaborative"
)

# Ensure you replace the placeholders
if SPOTIPY_CLIENT_ID == "YOUR_SPOTIFY_CLIENT_ID" or SPOTIPY_CLIENT_SECRET == "YOUR_SPOTIFY_CLIENT_SECRET":
    logging.warning("Please replace 'YOUR_SPOTIFY_CLIENT_ID' and 'YOUR_SPOTIFY_CLIENT_SECRET' with your actual Spotify Developer credentials in the script.")

app = FastAPI()

# Initialize SpotifyOAuth object
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SPOTIPY_SCOPE,
    show_dialog=True  # Force showing the authorization dialog
)

@app.get("/login")
async def login():
    """
    Endpoint to initiate the Spotify authorization flow.
    """
    auth_url = sp_oauth.get_authorize_url()
    return {"auth_url": auth_url}

@app.get("/callback")
async def callback(code: str = Query(None)):
    """
    Endpoint to handle the Spotify callback and exchange the authorization code for tokens.
    """
    if code:
        try:
            token_info = sp_oauth.get_access_token(code)
            if token_info:
                logging.info(f"Successfully retrieved tokens: {token_info}")
                # In a real application, you would store these tokens securely
                return {"access_token": token_info["access_token"], "refresh_token": token_info.get("refresh_token")}
            else:
                logging.error("Failed to get access token.")
                raise HTTPException(status_code=400, detail="Failed to get access token from Spotify")
        except Exception as e:
            logging.error(f"Error during token exchange: {e}")
            raise HTTPException(status_code=500, detail=f"Error during token exchange: {e}")
    else:
        raise HTTPException(status_code=400, detail="Authorization code not provided.")

@app.get("/test_token")
async def test_token(access_token: str = Query(...)):
    """
    Endpoint to test if a given access token is valid by fetching basic user info.
    **This is for testing purposes only and should be removed in production.**
    """
    import spotipy
    try:
        sp = spotipy.Spotify(auth=access_token)
        user = sp.me()
        return {"user_id": user["id"], "display_name": user.get("display_name")}
    except Exception as e:
        logging.error(f"Error using access token: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)










        

