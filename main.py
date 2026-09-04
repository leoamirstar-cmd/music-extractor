from fastapi import FastAPI, HTTPException
import json
import os
import httpx
import urllib.parse

app = FastAPI()

# تابع برای خواندن دیتابیس محلی
def load_songs():
    if os.path.exists("songs.json"):
        try:
            with open("songs.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

@app.get("/")
def home():
    return {"status": "Namira Hybrid Music Server is active!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    query_lower = q.lower().strip()
    songs_db = load_songs()
    
    # مرحله اول: جستجو در فایل محلی songs.json برای تطابق‌های دقیق یا کلیدواژه‌ها
    for key, track in songs_db.items():
        if key in query_lower:
            return {
                "url": track["url"],
                "title": track["title"],
                "query": q,
                "http_headers": {"User-Agent": "Mozilla/5.0"}
            }
    
    # مرحله دوم: اگر در فایل محلی نبود، استفاده از iTunes API برای جستجوی آزاد و بدون خطا روی رندر
    encoded_query = urllib.parse.quote(q)
    api_url = f"https://itunes.apple.com/search?term={encoded_query}&entity=song&limit=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    track = results[0]
                    preview_url = track.get("previewUrl")
                    track_name = track.get("trackName", q)
                    artist_name = track.get("artistName", "")
                    
                    if preview_url:
                        return {
                            "url": preview_url,
                    "title": f"{track_name} - {artist_name}",
                            "query": q,
                            "http_headers": {"User-Agent": "Mozilla/5.0"}
                        }
            
            raise HTTPException(status_code=404, detail="موزیک مورد نظر یافت نشد.")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
