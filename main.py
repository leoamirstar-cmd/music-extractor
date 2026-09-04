from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import glob
import os
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    url: str

@app.get("/")
def home():
    return {"status": "Server is running!"}

@app.post("/")
def extract_audio(item: Item):
    target_url = item.url.strip()

    if "spotify.com" in target_url:
        try:
            # اجرای spotdl و گرفتن دقیق خروجی خطا (stderr)
            result = subprocess.run(
                ["spotdl", target_url, "--output", "/tmp/"],
                capture_output=True,
                text=True,
                timeout=45
            )
            
            # اگر خطایی رخ داد، متن دقیقش رو برمی‌گردونیم تا ببینیم داستان چیه
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                return {"error": f"Spotdl Failed: {error_msg}"}
            
            files = glob.glob("/tmp/*.mp3")
            if files:
                latest_file = max(files, key=os.path.getctime)
                filename = os.path.basename(latest_file)
                song_name = filename.replace(".mp3", "").replace("_", " ")
                
                return {
                    "title": song_name,
                    "author": "Spotify Artist",
                    "audio_url": f"https://music-extractor.onrender.com/file/{filename}",
                    "duration": "180"
                }
            return {"error": "فایل MP3 توسط spotdl ایجاد نشد"}
            
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}

    # ساوندکلاد مثل قبل بدون مشکل با yt_dlp کار می‌کنه
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            return {
                "title": info.get('title', 'Music Track'),
                "author": info.get('uploader', 'Unknown Artist'),
                "audio_url": info.get('url', ''),
                "duration": str(info.get('duration', 0))
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/file/{filename}")
def get_file(filename: str):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")
