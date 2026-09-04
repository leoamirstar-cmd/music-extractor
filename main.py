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

    # ۱. پردازش لینک‌های اسپاتیفای
    if "spotify.com" in target_url:
        try:
            api_url = f"https://spotify-downloader9.p.rapidapi.com/downloadSong?songId={target_url}"
            # استفاده از API عمومی و مستقیم spotidown
            res = requests.get(f"https://spotidown.app/api/download-track?url={target_url}", headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                if data.get("url") or data.get("link"):
                    return {
                        "title": data.get("title") or data.get("name") or "Spotify Track",
                        "author": data.get("artist") or data.get("artists") or "Spotify Artist",
                        "audio_url": data.get("url") or data.get("link"),
                        "duration": str(data.get("duration", "0"))
                    }
        except Exception:
            pass

        # متد دوم پشتیبان برای اسپاتیفای
        try:
            res2 = requests.get(f"https://api.fabdl.com/spotify/get?url={target_url}", timeout=10).json()
            if res2.get("result"):
                result = res2["result"]
                gid = result.get("gid")
                id_val = result.get("id")
                
                convert_res = requests.get(f"https://api.fabdl.com/spotify/mp3-convert-task/{gid}/{id_val}", timeout=10).json()
                if convert_res.get("result") and convert_res["result"].get("download_url"):
                    return {
                        "title": result.get("name", "Spotify Track"),
                        "author": result.get("artists", "Unknown Artist"),
                        "audio_url": f"https://api.fabdl.com{convert_res['result']['download_url']}",
                        "duration": str(result.get("duration_ms", 0) // 1000)
                    }
        except Exception:
            pass

    # ۲. پردازش ساوندکلاد و سایر منابع با yt_dlp
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
        
