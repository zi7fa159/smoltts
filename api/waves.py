import os
from flask import Flask, request, send_file, jsonify
from smallest import Smallest

app = Flask(__name__)

# Retrieve the Smallest API key from environment variables
SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")

# Initialize the Smallest client
client = Smallest(api_key=SMALLEST_API_KEY)

@app.route("/api/tts", methods=["GET"])
def tts():
    # Extract the 'text' query parameter; default to a sample text if not provided
    text = request.args.get("text", "Hello, this is a test of the Smallest TTS service.")

    try:
        # Synthesize speech from the input text
        audio_bytes = client.synthesize(text, voice_id="emily", format="mp3")

        # Define the path to temporarily save the audio file
        file_path = "/tmp/tts_output.mp3"

        # Write the synthesized audio to the file
        with open(file_path, "wb") as audio_file:
            audio_file.write(audio_bytes)

        # Send the audio file as a response for download
        return send_file(file_path, mimetype="audio/mpeg", as_attachment=True, download_name="tts_output.mp3")

    except Exception as e:
        # Handle errors and return a JSON response with the error message
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
