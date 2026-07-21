from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel
import io
import scipy.io.wavfile as wavfile
from ..backends.kokoro_backend import KokoroTTSBackend

router = APIRouter(tags=["Stateless TTS"])

# Global instance of Kokoro to avoid reloading
kokoro_backend = KokoroTTSBackend()

class StatelessTTSRequest(BaseModel):
    text: str
    voice_id: str = "af_heart"  # Default Kokoro voice
    language: str = "en"

@router.post("/generate-direct")
async def generate_direct(request: StatelessTTSRequest):
    """
    Stateless endpoint: Generates TTS using Kokoro and returns a WAV file directly
    in the HTTP response. Does NOT save to database or disk.
    """
    try:
        # Construct the minimal voice prompt for Kokoro preset voice
        voice_prompt = {
            "preset_voice_id": request.voice_id
        }
        
        # Generate the audio array and sample rate
        audio_array, sample_rate = await kokoro_backend.generate(
            text=request.text,
            voice_prompt=voice_prompt,
            language=request.language
        )
        
        # Write numpy array to a bytes buffer as WAV
        buffer = io.BytesIO()
        wavfile.write(buffer, sample_rate, audio_array)
        buffer.seek(0)
        
        # Return directly as HTTP response
        return Response(content=buffer.read(), media_type="audio/wav")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
