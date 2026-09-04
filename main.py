from fastapi import FastAPI, HTTPException
import httpx
import re

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Music Extractor Server is running successfully!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    search_url = f"https://html.duckduckgo.com/html/?q={q}+دانلود+آهنگ+لینک+مستقیم"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(search_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch search results")
            
            html = response.text
            # جستجو برای تمام فرمت‌های صوتی (mp3, m4a, ogg, wav, aac)
            pattern = re.compile(r'href="(https?://[^"]+\.(mp3|m4a|ogg|wav|aac)[^"]*)"', re.IGNORECASE)
            matches = pattern.findall(html)
            
            if matches:
                # اولین لینک معتبر پیدا شده
                audio_url = matches[0][0]
                return {"url": audio_url, "query": q}
            
            # لینک پیش‌فرض پشتیبان در صورت عدم یافتن لینک مستقیم
            return {"url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "query": q}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
