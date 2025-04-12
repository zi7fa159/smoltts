import os
from flask import Flask, request, send_file, jsonify # Added jsonify for better error handling
import traceback # For logging detailed errors

# --- CORRECTED IMPORT based on the new library example ---
from smallestai.waves import WavesClient
# -------------------------------------------------------

app = Flask(__name__)

# Load API key from environment variables
SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")

@app.route("/api/waves", methods=["GET"])
def tts_endpoint():
    """Handle GET requests for text-to-speech optimized for ESP32 I2S streaming."""

    # Check if API Key was loaded (essential for Vercel deployment)
    if not SMALLEST_API_KEY:
        print("ERROR: SMALLEST_API_KEY environment variable not set.")
        return jsonify({"success": False, "message": "Server configuration error: API key missing."}), 500

    text = request.args.get("text", "Hello from the updated library!")
    voice_id = request.args.get("voice_id", "emily")  # Default voice

    print(f"Received request: text='{text}', voice_id='{voice_id}'") # Logging

    try:
        print("Initializing WavesClient...")
        # --- CORRECTED CLIENT INSTANTIATION ---
        client = WavesClient(api_key=SMALLEST_API_KEY)
        # ------------------------------------

        print("Synthesizing audio...")
        # Assuming synthesize still accepts these params and returns bytes when save_as is omitted
        audio_bytes = client.synthesize(
            text=text,                  # Use keyword arguments for clarity
            voice_id=voice_id,
            sample_rate=16000,          # ✅ Best for ESP32 I2S streaming
            add_wav_header=True        # ✅ Ensure correct WAV format
            # Do NOT use save_as here - we need the bytes for send_file
        )
        print(f"Audio synthesized successfully ({len(audio_bytes)} bytes).")

        # Save as a temporary WAV file (Vercel requires /tmp for writes)
        file_path = "/tmp/output.wav"
        print(f"Saving audio to {file_path}...")
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        print("Audio saved.")

        print("Sending file...")
        return send_file(
            file_path,
            mimetype="audio/wav",
            as_attachment=True,
            download_name="tts.wav"
        )

    except Exception as e:
        # Log the full error to Vercel logs for better debugging
        print(f"ERROR during TTS synthesis: {e}")
        print(traceback.format_exc()) # Print detailed traceback
        return jsonify({"success": False, "message": str(e)}), 500

# This block is for local testing only, Vercel uses the 'app' object directly.
if __name__ == "__main__":
     # Optional: Load .env for local testing if python-dotenv is installed
    try:
        from dotenv import load_dotenv
        load_dotenv()
        SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")
        if SMALLEST_API_KEY:
            print("Loaded API key from .env for local testing.")
        else:
             print("Warning: SMALLEST_API_KEY not found in .env or environment for local testing.")
    except ImportError:
        pass # Ignore if dotenv is not installed

    app.run(debug=True, port=5001)
