from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import requests
import re
import os
import glob
import uuid

app = FastAPI()

def get_spotify_info(url: str):
    try:
        # دریافت HTML صفحه اسپاتیفای برای استخراج عنوان و خواننده
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            title_match = re.search(r'<title>(.*?)</title>', res.text)
            if title_match:
                title_text = title_match.group(1)
                # حذف عبارت‌های اضافه‌ای مثل Spotify از عنوان
                clean_title = title_text.split('|')[0].replace(' - song and lyrics by ', ' ').replace(' | Spotify', '').strip()
                return clean_title
    except Exception:
        pass
    return None

@app.get("/")
def home():
    return {"status": "ok", "message": "Music Extractor Engine is Running!"}

@app.get("/extract")
def extract_audio(url: str):
    unique_id = str(uuid.uuid4())[:8]
    output_template = f"/tmp/song_{unique_id}.%(ext)s"
    
    search_target = url
    spotify_title = None

    # اگر لینک اسپاتیفای بود
    if "spotify.com" in url:
        spotify_title = get_spotify_info(url)
        if spotify_title:
            search_target = f"ytsearch1:{spotify_title}"
        else:
            search_target = f"ytsearch1:{url}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_target, download=True)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries'][0]
            else:
                video_info = info
                
            title = video_info.get('title', 'Unknown Title')
            artist = video_info.get('uploader', 'Unknown Artist')

            if spotify_title:
                title = spotify_title

        matching_files = glob.glob(f"/tmp/song_{unique_id}.*")
        if not matching_files:
            raise HTTPException(status_code=500, detail="File download failed")

        downloaded_file = matching_files[0]
        filename = os.path.basename(downloaded_file)

        return {
            "status": "success",
            "title": title,
            "artist": artist,
            "download_url": f"/download/{filename}"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = f"/tmp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type='audio/mpeg', filename=filename)
    raise HTTPException(status_code=404, detail="File not found")
