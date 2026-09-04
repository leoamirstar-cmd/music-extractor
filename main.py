from fastapi import FastAPI
import httpx
import urllib.parse

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Server is alive and running!"}

@app.get("/search")
async def search_music(q: str = "test"):
    api_url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)
        return {
            "query_received": q,
            "deezer_status": response.status_code,
            "data": response.json()
        }
