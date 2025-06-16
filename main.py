from fastapi import FastAPI, Request
import json
from parser import *
import os

app = FastAPI()

@app.get("/info")
def read_root():
    return {"message": "Server is running"}

@app.get("/files")
def list_files():
    return {"files": os.listdir()}

@app.post("/get_news")
async def get_news(request: Request):
    data = await request.json()

    api_id = data.get("api_id")
    api_hash = data.get("api_hash")
    git_token = data.get("git_token")
    drive_service = data.get("drive_service")

    try:
        result = await parse_news(api_id, api_hash, git_token, drive_service)
        return result  # Теперь это dict, который можно вернуть
    except Exception as e:
        logging.error(f"Ошибка в get_news: {e}")
        return {"status": "error", "message": str(e)}
