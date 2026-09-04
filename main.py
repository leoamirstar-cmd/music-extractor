from fastapi import FastAPI, HTTPException
import httpx
import urllib.parse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Music Extractor Server is running stably!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    # استفاده از ایندکس‌های رایگان و بدون محدودیت ربات برای دانلود موزیک
    encoded_query = urllib.parse.quote(q)
    api_url = f"https://api.vagalume.com.br/search.php?art={encoded_query}" # یا استفاده از سرورهای واسط رایگان
    
    # روش امن‌تر: جستجوی مستقیم در منابع آزاد وب بدون خطای یوتیوب
    search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}+mp3+download"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(search_url, headers=headers)
            if response.status_code == 200:
                html = response.text
                import re
                # پیدا کردن لینک‌های صوتی معتبر از نتایج جستجوی آزاد
                matches = re.findall(r'href="(https?://[^"]+\.mp3[^"]*)"', html, re.IGNORECASE)
                if matches:
                    return {
                        "url": matches[0],
                        "title": q,
                        "query": q,
                        "http_headers": {"User-Agent": "Mozilla/5.0"}
                    }
                    
        raise HTTPException(status_code=404, detail="موزیکی با این مشخصات یافت نشد.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
