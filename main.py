from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import yt_dlp
import re

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

def fetch_spotify_metadata(url: str):
    """استخراج عنوان و خواننده از متا تگ‌های اسپاتیفای بدون نیاز به API Key"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            title_match = re.search(r'<title>(.*?)</title>', res.text)
            if title_match:
                raw_title = title_match.group(1)
                clean_title = raw_title.split('|')[0].replace(' - song and lyrics by ', ' ').replace(' - song by ', ' ').strip()
                return clean_title
    except Exception:
        pass
    return None

@app.post("/")
def extract_audio(item: Item):
    target_url = item.url.strip()
    spotify_title = None

    # اگر لینک اسپاتیفای بود، نام ترک رو در می‌اریم و توی یوتیوب سرچ می‌کنیم
    if "spotify.com" in target_url:
        spotify_title = fetch_spotify_metadata(target_url)
        if spotify_title:
            target_url = f"ytsearch1:{spotify_title}"
        else:
            target_url = f"ytsearch1:{target_url}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            title = spotify_title if spotify_title else info.get('title', 'Music Track')
            uploader = info.get('uploader', 'Unknown Artist')
            audio_url = info.get('url', '')
            duration = str(info.get('duration', 0))

            return {
                "title": title,
                "author": uploader,
                "audio_url": audio_url,
                "duration": duration
            }
    except Exception as e:
        return {"error": f"خطا در استخراج: {str(e)}"}
