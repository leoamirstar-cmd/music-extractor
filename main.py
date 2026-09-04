from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import requests
import yt_dlp
import os
import glob
import uuid

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "message": "Music Extractor Engine is Running!"}

@app.get("/extract")
def extract_audio(url: str):
    unique_id = str(uuid.uuid4())[:8]
    output_template = f"/tmp/song_{unique_id}.%(ext)s"

    # اگر لینک اسپاتیفای باشد
    if "spotify.com" in url:
        try:
            # دریافت مستقیم اطلاعات و لینک از API واسط اسپاتیفای
            api_res = requests.get(f"https://api.v2.spotidown.app/download?url={url}", timeout=10)
            if api_res.status_code == 200:
                data = api_res.json()
                download_link = data.get("link")
                title = data.get("title", "Spotify Track")
                artist = data.get("artist", "Unknown Artist")

                if download_link:
                    # دانلود مستقیم فایل صوتی
                    audio_res = requests.get(download_link, timeout=30)
                    file_path = f"/tmp/song_{unique_id}.mp3"
                    with open(file_path, "wb") as f:
                        f.write(audio_res.content)

                    return {
                        "status": "success",
                        "title": title,
                        "artist": artist,
                        "download_url": f"/download/song_{unique_id}.mp3"
                    }
        except Exception:
            pass

    # برای ساوندکلاد و سایر پلتفرم‌ها
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
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', 'Unknown Artist')

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
