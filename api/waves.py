import os
from flask import Flask, request, send_file
from smallest import Smallest

app = Flask(__name__)

# Load API key from environment variables
SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")

@app.route("/api/waves", methods=["GET"])
def tts_endpoint():
    """Handle GET requests for text-to-speech optimized for ESP32 I2S streaming."""
    text = request.args.get("text", "Hello, world!")
    voice_id = request.args.get("voice_id", "emily")  # Default voice: "emily"
    
    try:
        client = Smallest(api_key=SMALLEST_API_KEY)
        audio_bytes = client.synthesize(
            text, 
            voice_id=voice_id,
            sample_rate=16000,  # ✅ Best for ESP32 I2S streaming
            add_wav_header=True  # ✅ Ensure correct WAV format
        )

        # Save as a temporary WAV file
        file_path = "/tmp/output.wav"
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        return send_file(file_path, mimetype="audio/wav", as_attachment=True, download_name="tts.wav")

    except Exception as e:
        return {"success": False, "message": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)
