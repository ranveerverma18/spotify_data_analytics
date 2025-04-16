import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'spotify_backend'))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import asyncio
import uvicorn

# Print current working directory
print("Current Working Directory:", os.getcwd())

# Imports from backend modules
from spotify_backend.oauth import get_spotify_auth_url, get_tokens, fetch_user_data
from spotify_backend.producer_script import send_data_to_kafka
from spotify_backend.consumer_script import consume_topic

# Create FastAPI app
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecret")

# Template setup (for HTML)
templates = Jinja2Templates(directory="spotify_backend/templates")

# MongoDB Chart Base
MONGODB_CHART_BASE = "https://charts.mongodb.com/charts-project-xxx/embed/charts?id=chart_id&user_id="

# Home page with HTML login button
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Spotify login route
@app.get("/login")
def login():
    url = get_spotify_auth_url()
    return RedirectResponse(url)

# Callback after Spotify login
@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found.")

    try:
        tokens = get_tokens(code)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        user_data = fetch_user_data(access_token)
        user_id = user_data["user_profile"]["id"]

        send_data_to_kafka(user_data, user_id)
        await asyncio.to_thread(consume_topic, user_id)

        redirect_url = f"{MONGODB_CHART_BASE}{user_id}"
        return RedirectResponse(redirect_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in callback flow: {str(e)}")

# Run server
if __name__ == "__main__":
    uvicorn.run("spotify_backend.fastapi_app:app", host="0.0.0.0", port=8000, reload=True)




