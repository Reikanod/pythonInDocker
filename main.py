
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    print("✅ main.py загружен")
    return {"message": "Server is running"}

