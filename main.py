import os
import urllib.parse
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Music API Server is running stably!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    # استفاده از سرویس امن و پایدار برای استخراج جریان صوتی
    target_api = f"https://pipedapi.kavin.rocks/search?q={urllib.parse.quote(q)}&filter=music_songs"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(target_api, headers=headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    video_id = items[0].get("videoId")
                    title = items[0].get("title", q)
                    
                    if video_id:
                        stream_res = await client.get(f"https://pipedapi.kavin.rocks/streams/{video_id}", headers=headers)
                        if stream_res.status_code == 200:
                            streams = stream_res.json().get("audioStreams", [])
                            if streams:
                                return {
                                    "url": streams[0].get("url"),
                                    "title": title,
                                    "query": q,
                                    "http_headers": {"User-Agent": "Mozilla/5.0"}
                                }
            
            raise HTTPException(status_code=404, detail="موزیکی یافت نشد.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
