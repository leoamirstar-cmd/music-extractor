from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
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

@app.post("/")
def extract_audio(item: Item):
    target_url = item.url.strip()

    # پردازش اسپاتیفای با کتابخانه اوپن‌سورس spotdl
    if "spotify.com" in target_url:
        try:
            # دریافت متادیتا و لینک با spotdl
            result = subprocess.run(
                ["spotdl", "url", target_url],
                capture_output=True,
                text=True,
                timeout=15
            )
            output = result.stdout.strip()
            
            # استخراج اطلاعات
            if "http" in output:
                lines = output.splitlines()
                yt_url = [line for line in lines if "http" in line][0]
                
                # دریافت لینک مستقیم صوت از لینک یوتیوب استخراج شده
                ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(yt_url, download=False)
                    return {
                        "title": info.get('title', 'Spotify Track'),
                        "author": info.get('uploader', 'Unknown Artist'),
                        "audio_url": info.get('url', ''),
                        "duration": str(info.get('duration', 0))
                    }
        except Exception as e:
            return {"error": f"ارور spotdl: {str(e)}"}

    # پردازش ساوندکلاد
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
        return {"error": f"خطا در استخراج: {str(e)}"}
        
