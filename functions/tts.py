import os
import asyncio
import aiofiles
import base64
from smallest import AsyncSmallest

async def synthesize_speech(text):
    api_key = os.getenv("WAVES_API_KEY")
    if not api_key:
        raise ValueError("Missing API Key")

    async with AsyncSmallest(api_key=api_key) as client:
        return await client.synthesize(text, format="mp3")

async def handler(event, context):
    query_params = event.get("queryStringParameters", {})
    text = query_params.get("text", "Hello")

    try:
        audio_bytes = await synthesize_speech(text)

        # Encode audio as Base64 for direct download
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "audio/mpeg",
                "Content-Disposition": f"attachment; filename=speech.mp3",
            },
            "body": audio_base64,
            "isBase64Encoded": True,
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
