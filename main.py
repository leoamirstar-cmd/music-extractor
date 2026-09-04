from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
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

    # ۱. پردازش اختصاصی اسپاتیفای (بدون نیاز به سرچ یوتیوب)
    if "spotify.com" in target_url:
        try:
            # استفاده از موتور API اختصاصی اسپاتیفای
            api_url = f"https://api.v2.spotidown.app/download?url={target_url}"
            response = requests.get(api_url, timeout=12)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") or data.get("link"):
                    return {
                        "title": data.get("title", "Spotify Song"),
                        "author": data.get("artist", "Unknown Artist"),
                        "audio_url": data.get("link"),
                        "duration": str(data.get("duration", "0"))
                    }
        except Exception:
            pass

    # ۲. پردازش ساوندکلاد و مابقی سایت‌ها با yt_dlp
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
                "duration": str(info.get('duration', 0))
            }
    except Exception as e:
        return {"error": f"خطا در استخراج: {str(e)}"}
        
