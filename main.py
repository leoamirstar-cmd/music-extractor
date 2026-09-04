from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="Namira Music Engine", version="2.1")

@app.get("/")
def read_root():
    return {
        "status": "Namira Music Engine is fully operational!",
        "version": "2.1"
    }

@app.get("/search")
async def search_music(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty")
    
    deezer_url = f"https://api.deezer.com/search?q={q}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(deezer_url)
            data = response.json()
            
            tracks = data.get("data", [])
            if not tracks:
                raise HTTPException(status_code=404, detail="آهنگی یافت نشد.")
            
            track = tracks[0]
            duration_sec = track.get("duration", 30)
            mins = duration_sec // 60
            secs = duration_sec % 60
            formatted_duration = f"{mins:02d}:{secs:02d}"
            
            return {
                "url": track.get("preview"),
                "title": track.get("title"),
                "author": track.get("artist", {}).get("name"),
                "duration": formatted_duration,
                "query": q
            }
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="خطا در ارتباط با موتور جستجو")
        except Exception as e:
            print(f"Search error: {e}")
            raise HTTPException(status_code=500, detail="خطای داخلی سرور")
            
