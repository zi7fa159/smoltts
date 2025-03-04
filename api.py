import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

def handler(event, context):
    # Get API key from environment variable
    API_KEY = os.getenv("WAVES_API_KEY")
    ENDPOINT = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"

    if not API_KEY:
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "message": "Missing WAVES_API_KEY!"}),
        }

    # Parse request parameters
    try:
        params = json.loads(event["body"])
        text = params.get("text")
        voice_id = params.get("voice_id", "emily")
    except:
        return {"statusCode": 400, "body": json.dumps({"success": False, "message": "Invalid request"})}

    if not text:
        return {"statusCode": 400, "body": json.dumps({"success": False, "message": "Text is required"})}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "voice_id": voice_id,
        "format": "mp3",
    }

    # Make request to Waves API
    response = requests.post(ENDPOINT, json=payload, headers=headers)

    if response.status_code == 200:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "audio/mpeg"},
            "body": response.content,
            "isBase64Encoded": True,
        }

    return {
        "statusCode": response.status_code,
        "body": json.dumps({"success": False, "message": response.text}),
    }
