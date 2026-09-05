from fastapi import FastAPI, HTTPException
import yt_dlp

app = FastAPI(title="Namira Music Engine", version="4.0")

@app.get("/")
def read_root():
    return {
        "status": "Namira Music Engine with YouTube Music is fully operational!",
        "version": "4.0",
        "usage": "Use /search?q=your_song_name to search"
    }

@app.get("/search")
@app.get("/search/")
async def search_music(q: str = ""):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty")
    
    # تنظیمات yt-dlp برای استخراج لینک مستقیم و متادیتای موزیک از یوتیوب
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1', # جستجوی اولین نتیجه مرتبط در یوتیوب
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # جستجو و استخراج اطلاعات ویدیو/موزیک به صورت مسدودنشده
            info = ydl.extract_info(f"ytsearch:{q}", download=False)
            
            if 'entries' in info and info['entries']:
                track_info = info['entries'][0]
            else:
                track_info = info

            if not track_info:
                raise HTTPException(status_code=404, detail="موزیک مورد نظر یافت نشد.")

            audio_url = track_info.get('url', '')
            title = track_info.get('title', q)
            uploader = track_info.get('uploader', 'نامیرا موزیک')
            duration_sec = track_info.get('duration', 180) # پیش‌فرض ۳ دقیقه اگر نبود
            
            if not isinstance(duration_sec, int):
                duration_sec = 180

            mins = duration_sec // 60
            secs = duration_sec % 60
            formatted_duration = f"{mins:02d}:{secs:02d}"

            return {
                "url": audio_url,
                "title": title,
                "author": uploader,
                "duration": formatted_duration,
                "query": q
            }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"YouTube extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail="خطای داخلی سرور در استخراج از یوتیوب")
        
