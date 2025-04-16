from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import asyncio
import uvicorn

# ✅ Corrected module imports based on your filenames
from python_script_for_oauth import get_spotify_auth_url, get_tokens, fetch_user_data
from producer_script import send_to_kafka
from consumer_script import consume_from_kafka

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecret")

MONGODB_CHART_BASE = "https://charts.mongodb.com/charts-project-xxx/embed/charts?id=chart_id&user_id="

@app.get("/")
def home():
    return {
        "message": "Welcome to the Spotify Analytics App!",
        "login_url": "/login"
    }

@app.get("/login")
def login():
    url = get_spotify_auth_url()
    return RedirectResponse(url)

@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found.")

    try:
        # 1. Exchange code for tokens
        tokens = get_tokens(code)
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # 2. Fetch user data
        user_data = fetch_user_data(access_token)
        user_id = user_data["user_profile"]["id"]

        # 3. Send to Kafka
        send_to_kafka(user_data, user_id)

        # 4. Trigger Kafka consumer to store in MongoDB
        await asyncio.to_thread(consume_from_kafka, user_id)

        # 5. Redirect to user's MongoDB chart
        redirect_url = f"{MONGODB_CHART_BASE}{user_id}"
        return RedirectResponse(redirect_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in callback flow: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



