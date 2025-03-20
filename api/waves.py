import os
import io
import re
from flask import Flask, request, send_file
from smallest import Smallest

app = Flask(__name__)

# Load API key from environment variables
SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")

def chunk_text(text, max_length=500):
    """
    Split text into chunks with proper sentence boundaries.
    
    Args:
        text: The input text to chunk
        max_length: Maximum length of each chunk (in characters)
        
    Returns:
        List of text chunks
    """
    # Short text doesn't need chunking
    if len(text) <= max_length:
        return [text]
    
    # Split by sentence endings (., !, ?)
    # Keep the punctuation with the sentence
    sentences = re.findall(r'[^.!?]+[.!?]', text)
    
    # Handle any remaining text without punctuation
    remainder = re.sub(r'.*[.!?]', '', text).strip()
    if remainder:
        sentences.append(remainder)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed max_length, 
        # start a new chunk (unless current_chunk is empty)
        if current_chunk and len(current_chunk) + len(sentence) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

@app.route("/api/waves", methods=["GET"])
def tts_endpoint():
    """Handle GET requests for text-to-speech optimized for ESP32 I2S streaming."""
    text = request.args.get("text", "Hello, world!")
    voice_id = request.args.get("voice_id", "emily")  # Default voice: "emily"
    
    # Check for chunking parameter, default to True for long text
    enable_chunking = request.args.get("chunking", "auto").lower()
    
    try:
        client = Smallest(api_key=SMALLEST_API_KEY)
        
        # Determine if chunking is needed
        should_chunk = (enable_chunking == "true" or 
                       (enable_chunking == "auto" and len(text) > 500))
        
        if should_chunk:
            # Split text into manageable chunks
            chunks = chunk_text(text)
            
            # Process each chunk and combine the audio
            combined_audio = io.BytesIO()
            
            # Process first chunk to get WAV header
            first_chunk = chunks.pop(0)
            first_audio = client.synthesize(
                first_chunk,
                voice_id=voice_id,
                sample_rate=16000,
                add_wav_header=True
            )
            
            # Write first chunk with header to our combined audio
            combined_audio.write(first_audio)
            
            # For remaining chunks, don't include WAV header to avoid corruption
            for chunk in chunks:
                chunk_audio = client.synthesize(
                    chunk,
                    voice_id=voice_id,
                    sample_rate=16000,
                    add_wav_header=False  # Skip WAV header for subsequent chunks
                )
                combined_audio.write(chunk_audio)
            
            # Prepare the combined audio for sending
            combined_audio.seek(0)
            
            return send_file(
                combined_audio, 
                mimetype="audio/wav",
                as_attachment=True,
                download_name="tts.wav"
            )
        else:
            # Process short text normally
            audio_bytes = client.synthesize(
                text, 
                voice_id=voice_id,
                sample_rate=16000,
                add_wav_header=True
            )
            
            # Create in-memory file instead of using tmp directory
            audio_file = io.BytesIO(audio_bytes)
            
            return send_file(
                audio_file,
                mimetype="audio/wav",
                as_attachment=True,
                download_name="tts.wav"
            )

    except Exception as e:
        return {"success": False, "message": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)
