from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
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
    return {"status": "Direct yt-dlp Extractor is running!"}

@app.post("/")
def extract_audio(item: Item):
    target_url = item.url.strip()
    
    # اگر لینک اسپاتیفای بود، متن رو تبدیل به کوئری سرچ می‌کنیم
    search_query = target_url
    if "spotify.com" in target_url:
        # اینجا می‌تونیم از روش مستقیم yt_dlp برای سرچ نام آهنگ استفاده کنیم
        search_query = f"ytsearch1:audio from spotify {target_url}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '/tmp/%(id)s.%(ext)s',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            return {
                "title": info.get('title', 'Music Track'),
                "author": info.get('uploader', 'Unknown Artist'),
                "audio_url": info.get('url', ''),
                "duration": str(int(info.get('duration', 0)))
            }
    except Exception as e:
        return {"error": f"Extraction Error: {str(e)}"}

@app.get("/file/{filename}")
def get_file(filename: str):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")
    
