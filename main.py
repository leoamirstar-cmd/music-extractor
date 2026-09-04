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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    # ۱. اسپاتیفای (مستقیم با API بدون یوتیوب)
    if "spotify.com" in target_url:
        # متد اول: FabDL
        try:
            res = requests.get(f"https://api.fabdl.com/spotify/get?url={target_url}", headers=headers, timeout=8).json()
            if res.get("result"):
                result = res["result"]
                gid = result.get("gid")
                id_val = result.get("id")
                convert_res = requests.get(f"https://api.fabdl.com/spotify/mp3-convert-task/{gid}/{id_val}", headers=headers, timeout=8).json()
                if convert_res.get("result") and convert_res["result"].get("download_url"):
                    return {
                        "title": result.get("name", "Spotify Track"),
                        "author": result.get("artists", "Unknown Artist"),
                        "audio_url": f"https://api.fabdl.com{convert_res['result']['download_url']}",
                        "duration": str(result.get("duration_ms", 0) // 1000)
                    }
        except Exception:
            pass

        # متد دوم: Cobalt
        try:
            cobalt_res = requests.post(
                "https://api.cobalt.tools/api/json",
                json={"url": target_url, "downloadMode": "audio"},
                headers={**headers, "Accept": "application/json"},
                timeout=8
            ).json()
            if cobalt_res.get("url"):
                return {
                    "title": "Spotify Music",
                    "author": "Spotify Artist",
                    "audio_url": cobalt_res.get("url"),
                    "duration": "180"
                }
        except Exception:
            pass

        return {"error": "امکان دریافت لینک اسپاتیفای وجود نداشت."}

    # ۲. ساوندکلاد و سایر سایت‌ها (استخراج مستقیم بدون یوتیوب)
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'force_generic_extractor': False
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                info = info['entries'][0]

            return {
                "title": info.get('title', 'SoundCloud Track'),
                "author": info.get('uploader', 'Unknown Artist'),
                "audio_url": info.get('url', ''),
                "duration": str(info.get('duration', 0))
            }
    except Exception as e:
        return {"error": f"خطا در استخراج: {str(e)}"}
        
