import os
from flask import Flask, request, send_file
from smallest import Smallest

app = Flask(__name__)

# Load API key from environment variables
SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")

def generate_tts(text):
    """Generate TTS and save it as an MP3 file."""
    client = Smallest(api_key=SMALLEST_API_KEY)
    audio_bytes = client.synthesize(text, voice_id="emily", format="mp3")

    file_path = "/tmp/output.mp3"
    with open(file_path, "wb") as f:
        f.write(audio_bytes)
    
    return file_path

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
