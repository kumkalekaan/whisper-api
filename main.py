from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import whisper
import yt_dlp
import os

app = FastAPI()

# Lazy loading - model ilk istekte yüklenecek!
model = None

@app.get("/")
def home():
    return {"status": "Whisper API çalışıyor!", "endpoint": "/transcribe?url=VIDEO_URL"}

@app.get("/transcribe")
async def transcribe(url: str = Query(..., description="Video URL")):
    global model
    
    # Model henüz yüklenmemişse yükle
    if model is None:
        model = whisper.load_model("tiny")  # tiny model = 75 MB RAM!
    
    audio_path = "/tmp/audio_" + str(os.getpid()) + ".mp3"
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        result = model.transcribe(audio_path, language="tr")
        transcript = result["text"]
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return JSONResponse({"success": True, "transcript": transcript})
        
    except Exception as e:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return JSONResponse({"error": str(e)}, status_code=500)
