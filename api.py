import os
import json
import requests
import base64

def handler(event, context):
    API_KEY = os.getenv("WAVES_API_KEY")
    ENDPOINT = "https://waves-api.smallest.ai/api/v1/lightning/get_speech"

    if not API_KEY:
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "message": "Missing WAVES_API_KEY!"}),
        }

    # Read query parameters from GET request
    query_params = event.get("queryStringParameters", {})
    text = query_params.get("text")
    voice_id = query_params.get("voice_id", "emily")

    if not text:
        return {
            "statusCode": 400,
            "body": json.dumps({"success": False, "message": "Text is required!"}),
        }

    # Send request to Waves API
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"text": text, "voice_id": voice_id, "format": "mp3"}

    response = requests.post(ENDPOINT, json=payload, headers=headers)

    if response.status_code == 200:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "audio/mpeg",
                "Content-Disposition": f'attachment; filename="speech.mp3"',
            },
            "body": base64.b64encode(response.content).decode("utf-8"),
            "isBase64Encoded": True,
        }

    return {
        "statusCode": response.status_code,
        "body": json.dumps({"success": False, "message": response.text}),
    }
