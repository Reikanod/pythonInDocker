from fastapi import FastAPI, Request
import json
from parser import *

app = FastAPI()

@app.get("/info")
def read_root():
    return {"message": "Server is running"}


@app.post("/get_news")
async def get_news(request: Request):
    data = await request.json()

    api_id = data.get("api_id")
    api_hash = data.get("api_hash")
    password = data.get("Password")
    
    input_data = json.dumps({
        "api_id": api_id,
        "api_hash": api_hash,
        "password": password
    })

 # Вызов parser.py
    return show_res(api_id, api_hash, password)

