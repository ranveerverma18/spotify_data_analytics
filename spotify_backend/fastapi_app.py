import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'spotify_backend'))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

# Import from backend modules
from spotify_backend.oauth import get_spotify_auth_url, get_tokens, fetch_user_data
from spotify_backend.producer_script import send_data_to_kafka

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecret")

# Template setup
templates = Jinja2Templates(directory="spotify_backend/templates")

# MongoDB Chart Base URL (Set up to accept user_id param in chart filter)
MONGODB_CHART_BASE = "https://charts.mongodb.com/charts-your-project-id/embed/charts?id=your-chart-id&theme=light&autoRefresh=true&user_id="

# Home page with login button
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Redirect to Spotify login
@app.get("/login")
def login():
    url = get_spotify_auth_url()
    return RedirectResponse(url)

# Callback route after Spotify auth
@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found.")

    try:
        # Get access + refresh tokens
        tokens = get_tokens(code)
        access_token = tokens["access_token"]

        # Fetch Spotify user data
        user_data = fetch_user_data(access_token)
        user_id = user_data["user_profile"]["id"]

        # Send user data to Kafka
        send_data_to_kafka(user_data)

        # Redirect to personalized MongoDB Chart
        redirect_url = f"{MONGODB_CHART_BASE}{user_id}"
        return RedirectResponse(redirect_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in callback flow: {str(e)}")

# Start the app with uvicorn
if __name__ == "__main__":
    uvicorn.run("spotify_backend.fastapi_app:app", host="0.0.0.0", port=8000, reload=True)






