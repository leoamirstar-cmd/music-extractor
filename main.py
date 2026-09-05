from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="Namira Music Engine", version="2.9")

@app.get("/")
def read_root():
    return {
        "status": "Namira Music Engine is fully operational!",
        "version": "2.9",
        "usage": "Use /search?q=your_song_name to search"
    }

@app.get("/search")
@app.get("/search/")
async def search_music(q: str = ""):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty")
    
    deezer_url = f"https://api.deezer.com/search?q={q}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(deezer_url)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="خطا از سمت سرور دیزر")
                
            data = response.json()
            tracks = data.get("data", [])
            if not tracks:
                raise HTTPException(status_code=404, detail="آهنگی یافت نشد.")
            
            track = tracks[0]
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
            
