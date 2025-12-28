from flask import Flask, request, jsonify
import whisper
import yt_dlp
import os

app = Flask(__name__)

# Whisper model yükle
model = whisper.load_model("base")

@app.route('/')
def home():
    return {"status": "Whisper API çalışıyor!", "endpoint": "/transcribe?url=VIDEO_URL"}

@app.route('/transcribe', methods=['POST', 'GET'])
def transcribe():
    url = request.args.get('url') or request.form.get('url')
    if request.is_json:
        url = request.json.get('url')
    
    if not url:
        return jsonify({"error": "URL gerekli!"}), 400
    
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
        
        return jsonify({"success": True, "transcript": transcript})
        
    except Exception as e:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return jsonify({"error": str(e)}), 500
