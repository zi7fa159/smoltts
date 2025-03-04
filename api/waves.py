import os
import io
from flask import Flask, request, send_file
from smallest import Smallest
from pydub import AudioSegment

app = Flask(__name__)

# Load API key from environment variables
SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")

def generate_tts(text):
    """Generate TTS and convert it to MP3."""
    client = Smallest(api_key=SMALLEST_API_KEY)
    audio_bytes = client.synthesize(text, voice_id="emily")  # Removed format="mp3"

    # Convert WAV bytes to MP3
    audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))
    mp3_path = "/tmp/output.mp3"
    audio.export(mp3_path, format="mp3")

    return mp3_path

@app.route("/api/waves", methods=["GET"])
def tts_endpoint():
    """Handle GET requests for text-to-speech."""
    text = request.args.get("text", "Hello, world!")

    try:
        file_path = generate_tts(text)
        return send_file(file_path, mimetype="audio/mp3", as_attachment=True, download_name="tts.mp3")
    except Exception as e:
        return {"success": False, "message": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)
