import os
from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Music Extractor Server is running stably!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': False,
    }

    try:
        # جستجو در یوتیوب
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{q} audio", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                audio_url = entry.get('url')
                title = entry.get('title', q)
                if audio_url:
                    return {
                        "url": audio_url,
                        "title": title,
                        "query": q,
                        # ارسال User-Agent مورد نیاز به کلاینت برای جلوگیری از خطای دسترسی
                        "http_headers": {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        }
                    }
                    
        # جستجو در ساوندکلاد به عنوان جایگزین
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"scsearch1:{q}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                audio_url = entry.get('url')
                title = entry.get('title', q)
                if audio_url:
                    return {
                        "url": audio_url,
                        "title": title,
                        "query": q,
                        "http_headers": {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                        }
                    }

        raise HTTPException(status_code=404, detail="لینک مستقیمی برای این آهنگ یافت نشد.")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
