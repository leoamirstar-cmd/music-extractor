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
    
    search_url = f"https://html.duckduckgo.com/html/?q={q}+دانلود+آهنگ"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(search_url, headers=headers)
            if response.status_code == 200:
                html = response.text
                # جستجو برای پیدا کردن لینک‌های صوتی معتبر
                pattern = re.compile(r'href="(https?://[^"]+\.(mp3|m4a|ogg|wav|aac)[^"]*)"', re.IGNORECASE)
                matches = pattern.findall(html)
                
                if matches:
                    audio_url = matches[0][0]
                    return {"url": audio_url, "query": q}
            
            # لینک پشتیبان پایدار اگر چیزی پیدا نشد
            return {"url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "query": q}
            
    except Exception as e:
        return {"url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", "query": q}
        
