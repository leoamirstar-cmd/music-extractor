import urllib.parse
from fastapi import FastAPI, HTTPException
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
    
    # جستجوی مستقیم در منابع آزاد وب برای یافتن فایل صوتی یا پخش‌کننده‌ها
    search_query = f"{q} آهنگ mp3"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                html_content = response.text
                
                # استخراج لینک‌های مستقیم صوتی یا صفحات معتبر پخش از نتایج
                urls = re.findall(r'href="(https?://[^"]+\.mp3[^"]*)"', html_content, re.IGNORECASE)
                
                if not urls:
                    # اگر لینک مستقیم mp3 نبود، به دنبال لینک‌های سایت‌های معتبر موزیک در نتایج بگرد
                    all_links = re.findall(r'uddg=([^&]+)', html_content)
                    for link in all_links:
                        decoded_link = urllib.parse.unquote(link)
                        if any(domain in decoded_link for domain in ['irangn', 'nex1music', 'musicsweb', 'tehranmusic', 'bia2music']):
                            return {
                                "url": decoded_link,
                                "title": q,
                                "query": q,
                                "http_headers": {"User-Agent": "Mozilla/5.0"}
                            }
                    
                    if all_links:
                        # اولین لینک معتبر جستجو به عنوان جایگزین
                        first_valid = urllib.parse.unquote(all_links[0])
                        return {
                            "url": first_valid,
                            "title": q,
                            "query": q,
                            "http_headers": {"User-Agent": "Mozilla/5.0"}
                        }
                else:
                    return {
                        "url": urls[0],
                        "title": q,
                        "query": q,
                        "http_headers": {"User-Agent": "Mozilla/5.0"}
                    }
            
            raise HTTPException(status_code=404, detail="موزیکی یافت نشد.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
