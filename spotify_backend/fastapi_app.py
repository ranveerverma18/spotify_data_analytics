import sys
import os
from pprint import pprint
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import requests
from pymongo import MongoClient

# --- YOUR MODULES ---
from spotify_backend.oauth import get_spotify_auth_url, get_tokens
from spotify_backend.producer_script import send_data_to_kafka

# --- FASTAPI SETUP ---
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecret")
templates = Jinja2Templates(directory="spotify_backend/templates")

# --- MONGODB SETUP ---
MONGO_URI = "mongodb+srv://ranveerverma18:ranveer18@cluster0.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["spotify_app"]
collection = db["users_data"]

# --- CHART DASHBOARD BASE URL ---
MONGODB_CHART_BASE = (
    "https://charts.mongodb.com/charts-project-0-pnhfwmx/embed/dashboards"
    "?id=f34a04e3-a172-4c15-89be-05f7de03c0a3&theme=light"
    "&autoRefresh=true&maxDataAge=3600&showTitleAndDesc=false"
    "&scalingWidth=fixed&scalingHeight=fixed"
)

# --- LOGGER ---
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
def login():
    return RedirectResponse(get_spotify_auth_url())

def fetch_user_data(access_token):
    url = "https://api.spotify.com/v1/me"
    headers = { "Authorization": f"Bearer {access_token}" }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch user data: {response.text}")
        raise Exception(f"Spotify API error: {response.text}")

# Callback route after Spotify auth
@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        logger.error("Authorization code not found.")
        raise HTTPException(status_code=400, detail="Authorization code not found.")

    try:
        # Get access token and refresh token correctly
        tokens = get_tokens(code)
        access_token = tokens["access_token"]
        refresh_token = tokens.get("refresh_token")  # Optionally handle the refresh_token

        # Fetch user data and log it for debugging
        user_data = fetch_user_data(access_token)
        logger.debug(f"Fetched user data: {user_data}")  # Add logging to check the response structure

        # Check if the response is a dictionary as expected
        if not isinstance(user_data, dict):
            logger.error("User data is not in the expected dictionary format.")
            raise HTTPException(status_code=500, detail="User data is not in the expected dictionary format")

        if "user_profile" not in user_data or "id" not in user_data["user_profile"]:
            logger.error("Invalid user data structure received from Spotify.")
            raise HTTPException(status_code=500, detail="Invalid user data structure received from Spotify")

        user_id = user_data["user_profile"]["id"]

        # Send the data to Kafka
        try:
            send_data_to_kafka(user_data)
        except Exception as e:
            logger.error(f"Error sending data to Kafka: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error sending data to Kafka: {str(e)}")

        # Construct the personalized MongoDB chart URL
        chart_url = f"https://charts.mongodb.com/charts-project-0-pnhfwmx/embed/dashboards?id=f34a04e3-a172-4c15-89be-05f7de03c0a3&theme=light&autoRefresh=true&maxDataAge=3600&showTitleAndDesc=false&scalingWidth=fixed&scalingHeight=fixed#user_id={user_id}"

        # Return the template with the personalized chart
        return templates.TemplateResponse("dashboard.html", {"request": request, "chart_url": chart_url})

    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in callback flow: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("spotify_backend.fastapi_app:app", host="0.0.0.0", port=8000, reload=True)














