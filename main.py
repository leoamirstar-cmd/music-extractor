from fastapi import FastAPI, HTTPException
import httpx
import urllib.parse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Namira Clean Music Server is active!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    # جستجوی دقیقاً همون چیزی که کاربر سرچ کرده در آرشیو جهانی
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
            
            # اگر پیدا نشد، هیچ آهنگ فیکی نمی‌فرستیم و خطای تمیز 404 برمی‌گردانیم
            raise HTTPException(status_code=404, detail="موزیک مورد نظر یافت نشد.")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
