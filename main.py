from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="Namira Music Engine", version="3.1")

@app.get("/")
def read_root():
    return {
        "status": "Namira Music Engine is fully operational!",
        "version": "3.1",
        "usage": "Use /search?q=your_song_name to search"
    }

@app.get("/search")
@app.get("/search/")
async def search_music(q: str = ""):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        track = None
        try:
            # مرحله اول: جستجو در دیزر
            deezer_url = f"https://api.deezer.com/search?q={q}"
            response = await client.get(deezer_url)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("data", [])
                if tracks:
                    track = tracks[0]
            
            # مرحله دوم: اگر در دیزر پیدا نشد، اتصال به سورس جایگزین آزاد (بدون مسدودی روی رندر)
            if not track:
                # استفاده از ایندکس‌کننده یا سرور کمکی امن برای موزیک‌های ایرانی
                alt_url = f"https://api-v2.soundcloud.com/search/tracks?q={q}&client_id=YOUR_CLIENT_ID"
                # چون ساندکلود کلید می‌خواهد، از یک پروکسی عمومی یا API متن‌باز استفاده می‌کنیم:
                fallback_url = f"https://itunes.apple.com/search?term={q}&media=music&limit=1"
                
                alt_response = await client.get(fallback_url)
                if alt_response.status_code == 200:
                    alt_data = alt_response.json()
                    results = alt_data.get("results", [])
                    if results:
                        item = results[0]
                        track = {
                            "preview": item.get("previewUrl", ""),
                            "title": item.get("trackName", q),
                            "artist": {"name": item.get("artistName", "نامیرا موزیک")},
                            "duration": 30
                        }

            if not track:
                raise HTTPException(status_code=404, detail="موزیک مورد نظر در هیچ‌کدام از آرشیوها یافت نشد.")
            
            duration_sec = track.get("duration", 30)
            if not isinstance(duration_sec, int):
                duration_sec = 30
                
            mins = duration_sec // 60
            secs = duration_sec % 60
            formatted_duration = f"{mins:02d}:{secs:02d}"
            
            artist_info = track.get("artist")
            author_name = artist_info.get("name", "نامیرا موزیک") if isinstance(artist_info, dict) else "نامیرا موزیک"
            
            return {
                "url": track.get("preview", ""),
                "title": track.get("title", q),
                "author": author_name,
                "duration": formatted_duration,
                "query": q
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            print(f"Server crash error: {str(e)}")
            raise HTTPException(status_code=500, detail="خطای داخلی سرور")
