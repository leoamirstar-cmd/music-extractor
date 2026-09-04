from fastapi import FastAPI, HTTPException
import httpx
import re

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Music Extractor Server is running stably!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    # جستجو در منابع عمومی وب برای یافتن لینک مستقیم آهنگ
    search_url = f"https://html.duckduckgo.com/html/?q={q}+دانلود+آهنگ+mp3+لینک+مستقیم"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(search_url, headers=headers)
            if response.status_code == 200:
                html = response.text
                # پیدا کردن تمام لینک‌های مستقیم صوتی معتبر در صفحات وب
                pattern = re.compile(r'href="(https?://[^"]+\.mp3[^"]*)"', re.IGNORECASE)
                matches = pattern.findall(html)
                
                if matches:
                    # فیلتر کردن لینک‌های نامعتبر یا تبلیغاتی
                    for url in matches:
                        if "download" in url or "dl" in url or "music" in url or "s1" in url or "s2" in url:
                            return {"url": url, "title": q, "query": q}
                    return {"url": matches[0], "title": q, "query": q}
            
            raise HTTPException(status_code=404, detail="لینک مستقیمی برای این آهنگ یافت نشد.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
