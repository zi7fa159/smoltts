import os
import io
import re
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
from smallest import Smallest
from typing import Optional

app = FastAPI()

# Load API key from environment variables
SMALLEST_API_KEY = os.getenv("SMALLEST_API_KEY")

def chunk_text(text, max_length=200):
    """
    Split text into smaller chunks with proper sentence boundaries.
    
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

@app.get("/api/waves")
async def tts_endpoint(
    text: str = Query("Hello, world!", description="Text to convert to speech"),
    voice_id: str = Query("emily", description="Voice ID to use"),
    chunking: Optional[str] = Query("auto", description="Chunking mode: 'auto', 'true', or 'false'")
):
    """
    Generate text-to-speech audio optimized for ESP32 I2S streaming.
    Returns a WAV file with the synthesized speech.
    """
    if not SMALLEST_API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        client = Smallest(api_key=SMALLEST_API_KEY)
        
        # Use smaller chunks (200 chars) to reduce processing time per chunk
        should_chunk = (chunking.lower() == "true" or 
                       (chunking.lower() == "auto" and len(text) > 200))
        
        if should_chunk:
            # Split text into smaller manageable chunks
            chunks = chunk_text(text, max_length=200)
            
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
            
            return StreamingResponse(
                combined_audio,
                media_type="audio/wav",
                headers={"Content-Disposition": "attachment; filename=tts.wav"}
            )
        else:
            # Process short text normally
            audio_bytes = client.synthesize(
                text, 
                voice_id=voice_id,
                sample_rate=16000,
                add_wav_header=True
            )
            
            # Create in-memory file
            audio_file = io.BytesIO(audio_bytes)
            audio_file.seek(0)
            
            return StreamingResponse(
                audio_file,
                media_type="audio/wav",
                headers={"Content-Disposition": "attachment; filename=tts.wav"}
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
