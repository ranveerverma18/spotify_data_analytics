import sys
import os
from pprint import pprint  # For debugging

sys.path.append(os.path.join(os.path.dirname(__file__), 'spotify_backend'))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
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

# MongoDB Dashboard Embed Base URL (Before #user_id=)
MONGODB_CHART_BASE = (
    "https://charts.mongodb.com/charts-project-0-pnhfwmx/embed/dashboards"
    "?id=f34a04e3-a172-4c15-89be-05f7de03c0a3&theme=light"
    "&autoRefresh=true&maxDataAge=3600&showTitleAndDesc=false"
    "&scalingWidth=fixed&scalingHeight=fixed"
)

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
        # ✅ FIXED: get access token as a string
        access_token = get_tokens(code)

        # Fetch user data
        user_data = fetch_user_data(access_token)
        pprint(user_data)

        if "user_profile" not in user_data or "id" not in user_data["user_profile"]:
            raise HTTPException(status_code=500, detail="Invalid user data structure received from Spotify")

        user_id = user_data["user_profile"]["id"]

        send_data_to_kafka(user_data)

        chart_url = f"{MONGODB_CHART_BASE}#user_id={user_id}"

        return templates.TemplateResponse("dashboard.html", {"request": request, "chart_url": chart_url})

    except Exception as e:
        print(f"Callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in callback flow: {str(e)}")


# Start the app with uvicorn
if __name__ == "__main__":
    uvicorn.run("spotify_backend.fastapi_app:app", host="0.0.0.0", port=8000, reload=True)









