import os
from fastapi import FastAPI, Query
import requests
from fastapi.responses import Response
from dotenv import load_dotenv

# Load environment variables from a .env file (useful for local testing)
load_dotenv()

app = FastAPI()

# Get API Key from environment variables
API_KEY = os.getenv("WAVES_API_KEY")
ENDPOINT = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"

if not API_KEY:
    raise ValueError("Missing WAVES_API_KEY environment variable!")

@app.get("/api/waves")
async def generate_tts(text: str = Query(..., min_length=1), voice_id: str = "emily"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "voice_id": voice_id,
        "format": "mp3",
    }

    # Send request to Smallest AI
    response = requests.post(ENDPOINT, json=payload, headers=headers)

    if response.status_code == 200:
        return Response(content=response.content, media_type="audio/mpeg")

    return {"success": False, "message": f"Error {response.status_code}: {response.text}"}
