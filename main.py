from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Advanced Music Extractor Server is running!"}

@app.get("/search")
async def search_music(q: str):
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    # جستجو همزمان در یوتیوب و ساوندکلاد با استفاده از yt-dlp
    search_query = f"ytsearch1:{q} audio"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # جستجو و استخراج اطلاعات
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                audio_url = entry.get('url')
                title = entry.get('title', q)
                
                if audio_url:
                    return {
                        "url": audio_url,
                        "title": title,
                        "query": q
                    }
                    
        # اگر از یوتیوب پیدا نشد، جستجو در ساوندکلاد
        sc_search_query = f"scsearch1:{q}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(sc_search_query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                entry = info['entries'][0]
                audio_url = entry.get('url')
                title = entry.get('title', q)
                if audio_url:
                    return {
                        "url": audio_url,
                        "title": title,
                        "query": q
                    }

        raise HTTPException(status_code=404, detail="موزیکی با این مشخصات پیدا نشد.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در سرور: {str(e)}")
        
