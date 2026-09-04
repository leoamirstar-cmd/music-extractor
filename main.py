from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import glob
import os
import yt_dlp

# ایمپورت کردن ماژول‌های استاندارد خود spotdl که توی کدهات دیدیم
from spotdl import Spotdl

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
    return {"status": "Spotify & SoundCloud Bridge is running!"}

@app.post("/")
def extract_audio(item: Item):
    target_url = item.url.strip()

    # ۱. پردازش لینک‌های اسپاتیفای با استفاده مستقیم از کلاس Spotdl و اجبار به استفاده از ساندکلاد
    if "spotify.com" in target_url:
        try:
            # ایجاد نمونه از Spotdl با تنظیمات اجبار به ساندکلاد برای دور زدن بلاک یوتیوب روی Render
            spotdl_instance = Spotdl(
                client_id=None,
                client_secret=None,
                downloader_settings={
                    "audio_providers": ["soundcloud"],
                    "output": "/tmp/{track-name}.{output-ext}"
                }
            )
            
            # جستجوی آهنگ
            songs = spotdl_instance.search([target_url])
            if not songs:
                return {"error": "آهنگ مورد نظر در اسپاتیفای پیدا نشد."}
            
            # دانلود آهنگ به پوشه /tmp/
            downloaded_songs = spotdl_instance.download_songs(songs)
            
            if downloaded_songs and downloaded_songs[0][1]:
                file_path = downloaded_songs[0][1]
                filename = os.path.basename(file_path)
                song_obj = downloaded_songs[0][0]
                
                return {
                    "title": song_obj.name,
                    "author": ", ".join(song_obj.artists),
                    "audio_url": f"https://music-extractor.onrender.com/file/{filename}",
                    "duration": str(int(song_obj.duration or 180))
                }
            
            return {"error": "خطا در دانلود فایل صوتی از طریق پل ساندکلاد."}
            
        except Exception as e:
            return {"error": f"Spotdl Exception: {str(e)}"}

    # ۲. پردازش لینک‌های ساوندکلاد مستقیم با yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            return {
                "title": info.get('title', 'Music Track'),
                "author": info.get('uploader', 'Unknown Artist'),
                "audio_url": info.get('url', ''),
                "duration": str(int(info.get('duration', 0)))
            }
    except Exception as e:
        return {"error": f"SoundCloud Error: {str(e)}"}

@app.get("/file/{filename}")
def get_file(filename: str):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
    raise HTTPException(status_code=404, detail="File not found")
