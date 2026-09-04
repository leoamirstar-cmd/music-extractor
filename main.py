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
    
    # جستجوی مستقیم در سایت‌های معتبر موزیک ایرانی از طریق موتور جستجو
    search_query = f"{q} سایت موزیک mp3"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                html_content = response.text
                
                # پیدا کردن لینک‌های مستقیم mp3 در نتایج
                mp3_matches = re.findall(r'href="(https?://[^"]+\.mp3[^"]*)"', html_content, re.IGNORECASE)
                if mp3_matches:
                    return {
                        "url": mp3_matches[0],
                        "title": q,
                        "query": q,
                        "http_headers": {"User-Agent": "Mozilla/5.0"}
                    }
                
                # استخراج لینک سایت‌های موزیک ایرانی از توکن‌های جستجو
                uddg_links = re.findall(r'uddg=([^&]+)', html_content)
                for link in uddg_links:
                    decoded_link = urllib.parse.unquote(link)
                    # بررسی اینکه لینک مربوط به سایت‌های دانلود موزیک باشد
                    if any(domain in decoded_link for domain in ['nex1music', 'tehranmusic', 'musicsweb', 'bia2music', 'irangn', 'upmusics']):
                        # ورود به صفحه و استخراج لینک دانلود داخلی
                        sub_res = await client.get(decoded_link, headers=headers)
                        if sub_res.status_code == 200:
                            sub_mp3 = re.findall(r'href="(https?://[^"]+\.mp3[^"]*)"', sub_res.text, re.IGNORECASE)
                            if sub_mp3:
                                return {
                                    "url": sub_mp3[0],
                                    "title": q,
                                    "query": q,
                                    "http_headers": {"User-Agent": "Mozilla/5.0"}
                                }
        
        # اگر واقعاً پیدا نشد، بدون فایل تست، خطای 404 برمی‌گردانیم تا فلاتر بفهمد
        raise HTTPException(status_code=404, detail="آهنگ مورد نظر یافت نشد.")
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
