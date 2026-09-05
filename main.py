from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="Namira Music Engine", version="4.1")

@app.get("/")
def read_root():
    return {
        "status": "Namira Music Engine is fully operational!",
        "version": "4.1",
        "usage": "Use /search?q=your_song_name to search"
    }

@app.get("/search")
@app.get("/search/")
async def search_music(q: str = ""):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty")
    
    # استفاده از iTunes API به عنوان یک منبع پایدار و بدون مسدودی روی سرور ابری
    itunes_url = f"https://itunes.apple.com/search?term={q}&media=music&limit=1"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(itunes_url)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="خطا از سمت سرور موزیک")
                
            data = response.json()
            results = data.get("results", [])
            if not results:
                raise HTTPException(status_code=404, detail="موزیک مورد نظر یافت نشد.")
            
            item = results[0]
            
            return {
                "url": item.get("previewUrl", ""),
                "title": item.get("trackName", q),
                "author": item.get("artistName", "نامیرا موزیک"),
                "duration": "00:30",
                "query": q
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            print(f"Server crash error: {str(e)}")
            raise HTTPException(status_code=500, detail="خطای داخلی سرور")
            
