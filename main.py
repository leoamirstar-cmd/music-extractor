from fastapi import FastAPI, HTTPException
import httpx
import urllib.parse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Namira Music Engine is fully operational!", "version": "2.1"}

@app.get("/search")
@app.get("/search/")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    clean_query = q.strip()
    api_url = f"https://api.deezer.com/search?q={urllib.parse.quote(clean_query)}"
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get("data", [])
                
                if tracks:
                    track = tracks[0]
                    preview_url = track.get("preview")
                    track_title = track.get("title", clean_query)
                    artist_name = track.get("artist", {}).get("name", "نامیرا موزیک")
                    duration_sec = track.get("duration", 30)
                    
                    # تبدیل ثانیه به فرمت mm:ss
                    mins = duration_sec // 60
                    secs = duration_sec % 60
                    formatted_duration = f"{mins:02d}:{secs:02d}"
                    
                    if preview_url:
                        return {
                            "url": preview_url,
                            "title": track_title,
                            "author": artist_name,
                            "duration": formatted_duration,
                            "query": clean_query
                        }
            
            raise HTTPException(status_code=404, detail="موزیک مورد نظر یافت نشد.")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطای داخلی سرور: {str(e)}")
        
