from fastapi import FastAPI, HTTPException
import urllib.parse
import httpx
import re

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Namira Music Server is active!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    # جستجوی مهندسی‌شده در منابع آزاد متن‌باز موزیک برای گرفتن لینک مستقیم
    encoded_query = urllib.parse.quote(q)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}+موزیک+mp3"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                html_content = response.text
                # استخراج لینک مستقیم mp3 از نتایج
                urls = re.findall(r'href="(https?://[^"]+\.mp3[^"]*)"', html_content, re.IGNORECASE)
                if urls:
                    return {
                        "url": urls[0],
                        "title": q,
                        "query": q,
                        "http_headers": {"User-Agent": "Mozilla/5.0"}
                    }
                
                # استخراج لینک‌های کمکی در صورت نبود فایل مستقیم
                uddg_links = re.findall(r'uddg=([^&]+)', html_content)
                for link in uddg_links:
                    decoded = urllib.parse.unquote(link)
                    if 'dl' in decoded or 'music' in decoded or 'download' in decoded:
                        return {
                            "url": decoded,
                            "title": q,
                            "query": q,
                            "http_headers": {"User-Agent": "Mozilla/5.0"}
                        }
        
        # اگر هیچ‌کدام پیدا نشد، به عنوان آخرین سنگر یک لینک صوتی واقعی متناسب با جستجو یا پیش‌فرض می‌فرستیم تا اپ متوقف نشود
        raise HTTPException(status_code=404, detail="لینک آهنگ پیدا نشد")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
