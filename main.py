from fastapi import FastAPI, HTTPException
import httpx
import urllib.parse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Namira Smart Music Server is active!"}

@app.get("/search")
@app.get("/search/")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    # دیکشنری نگاشت کلمات کلیدی فارسی یا تکه‌ای به کلیدواژه‌های معتبر جهانی
    # این قسمت به مرور قابل توسعه است تا هر کلمه عامیانه یا فارسی را هندل کند
    query_lower = q.lower().strip()
    
    # جستجو در Deezer API
    api_url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(api_url)
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("data", [])
                
                # اگر نتیجه مستقیم پیدا شد
                if tracks:
                    track = tracks[0]
                    preview_url = track.get("preview")
                    track_title = track.get("title", q)
                    artist_name = track.get("artist", {}).get("name", "")
                    
                    if preview_url:
                        return {
                            "url": preview_url,
                            "title": f"{track_title} - {artist_name}",
                            "query": q,
                            "http_headers": {"User-Agent": "Mozilla/5.0"}
                        }
            
            # اگر با عبارت اصلی چیزی پیدا نشد، به عنوان پشتیبان کلمات اضافه را می‌بریم یا ارور تمیز میدهیم
            raise HTTPException(status_code=404, detail="موزیک مورد نظر یافت نشد.")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
