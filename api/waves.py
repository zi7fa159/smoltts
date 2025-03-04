import os
import json
import asyncio
from smallest import AsyncSmallest
from flask import Flask, request, send_file

app = Flask(__name__)

# Get API key from environment variables
SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")

async def generate_tts(text):
    client = AsyncSmallest(api_key=SMALLEST_API_KEY)
    async with client as tts:
        audio_bytes = await tts.synthesize(text, voice_id="emily", format="mp3")

        # Save the audio to a file
        file_path = "/tmp/output.mp3"
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        
        return file_path

@app.route("/api/waves", methods=["GET"])
def tts_endpoint():
    text = request.args.get("text", "Hello, world!")
    
    # Generate TTS using asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    file_path = loop.run_until_complete(generate_tts(text))

    # Return the MP3 file for download
    return send_file(file_path, mimetype="audio/mp3", as_attachment=True, download_name="tts.mp3")

if __name__ == "__main__":
    app.run(debug=True)
