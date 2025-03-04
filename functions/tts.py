import os
import base64
import smallest_waves
from smallest_waves import WavesClient

def handler(event, context):
    # Get API Key from environment variables
    API_KEY = os.getenv("WAVES_API_KEY")
    if not API_KEY:
        return {"statusCode": 500, "body": "Missing API Key"}

    # Get text input from GET request
    query_params = event.get("queryStringParameters", {})
    text = query_params.get("text", "Hello")
    voice_id = query_params.get("voice_id", "emily")  # Default voice

    try:
        # Initialize Waves API Client
        waves = WavesClient(api_key=API_KEY)

        # Generate speech
        response = waves.get_speech(text=text, voice_id=voice_id, format="mp3")

        # Encode audio to Base64 for direct download
        audio_base64 = base64.b64encode(response).decode("utf-8")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "audio/mpeg",
                "Content-Disposition": f"attachment; filename=speech.mp3",
            },
            "body": audio_base64,
            "isBase64Encoded": True,  # Required for binary response
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
