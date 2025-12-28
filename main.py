from fastapi import FastAPI, HTTPException
from faster_whisper import WhisperModel
import yt_dlp
import os
import uvicorn

app = FastAPI()

# Whisper model (ilk çağrıda yüklenir)
model = None

def get_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = WhisperModel("base", device="cpu", compute_type="int8")
    return model

@app.get("/")
async def root():
    return {"status": "Whisper API is running!", "endpoint": "/transcribe?url=VIDEO_URL"}

@app.post("/transcribe")
async def transcribe(url: str):
    audio_path = "/tmp/audio.mp3"
    
    try:
        # 1. Video indir (audio only)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 2. Transcript çıkar
        whisper_model = get_model()
        segments, info = whisper_model.transcribe(audio_path, language="tr")
        transcript = " ".join([s.text for s in segments])
        
        # 3. Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {
            "success": True,
            "transcript": transcript,
            "language": info.language,
            "duration": info.duration
        }
        
    except Exception as e:
        # Cleanup on error
        if os.path.exists(audio_path):
            os.remove(audio_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
