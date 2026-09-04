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

@app.get("/")
def home():
    return {"status": "Server is running online!"}

@app.post("/")
def extract_audio(item: Item):
    target_url = item.url.strip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # ۱. پردازش اسپاتیفای با سرویس باکیفیت و مستقیم spotidownload
    if "spotify.com" in target_url:
        try:
            # دریافت اطلاعات متادیتای ترک
            info_res = requests.post(
                "https://spotidownloader.com/api/get-metadata",
                json={"url": target_url},
                headers=headers,
                timeout=10
            )
            if info_res.status_code == 200:
                data = info_res.json()
                download_res = requests.post(
                    "https://spotidownloader.com/api/download-track",
                    json={"url": target_url},
                    headers=headers,
                    timeout=12
                )
                if download_res.status_code == 200:
                    dl_data = download_res.json()
                    audio_link = dl_data.get("fileUrl") or dl_data.get("link") or dl_data.get("url")
                    if audio_link:
                        return {
                            "title": data.get("title", "Spotify Track"),
                            "author": data.get("artist", "Unknown Artist"),
                            "audio_url": audio_link,
                            "duration": str(data.get("duration", 180))
                        }
        except Exception:
            pass

        # متد پشتیبان مستقیم
        try:
            fallback_res = requests.get(
                f"https://api.spotidown.app/download?url={target_url}",
                headers=headers,
                timeout=10
            ).json()
            if fallback_res.get("link"):
                return {
                    "title": fallback_res.get("title", "Spotify Track"),
                    "author": fallback_res.get("artist", "Unknown Artist"),
                    "audio_url": fallback_res.get("link"),
                    "duration": str(fallback_res.get("duration", 0))
                }
        except Exception:
            pass

        return {"error": "امکان استخراج فایل صوتی اسپاتیفای وجود نداشت."}

    # ۲. پردازش ساوندکلاد و سایر سرویس‌ها با yt_dlp
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
        
