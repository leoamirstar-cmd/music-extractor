import os
import urllib.parse
from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Music API Proxy is running stably!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    encoded_query = urllib.parse.quote(q)
    
    # استفاده از ایندکس‌های جستجوی امن صوتی یا سرویس‌های واسط عمومی
    # به جای درگیری مستقیم با یوتیوب، از پروکسی‌های متن‌باز استریم استفاده می‌کنیم
    target_api = f"https://pipedapi.kavin.rocks/search?q={urllib.parse.quote(q + ' audio')}&filter=music_songs"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(target_api, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if items:
                    # پیدا کردن اولین نتیجه موزیک معتبر
                    first_item = items[0]
                    videoId = first_item.get("videoId")
                    title = first_item.get("title", q)
                    
                    if videoId:
                        # گرفتن لینک استریم مستقیم و پایدار از طریق سرویس‌های آزاد Piped
                        stream_url = f"https://piped-api.kavin.rocks/streams/{videoId}"
                        stream_res = await client.get(stream_url, headers=headers)
                        
                        if stream_res.status_code == 200:
                            stream_data = stream_res.json()
                            audio_streams = stream_data.get("audioStreams", [])
                            
                            if audio_streams:
                                # انتخاب بهترین کیفیت صوتی موجود
                                best_audio = audio_streams[0]
                                direct_url = best_audio.get("url")
                                
                                if direct_url:
                                    return {
                                        "url": direct_url,
                                        "title": title,
                                        "query": q,
                                        "http_headers": {
                                            "User-Agent": "Mozilla/5.0"
                                        }
                                    }
            
            # اگر از روش بالا نتیجه نگرفتیم، بازگشت به حالت پشتیبان امن
            raise HTTPException(status_code=404, detail="موزیکی با این مشخصات یافت نشد.")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy Error: {str(e)}")
