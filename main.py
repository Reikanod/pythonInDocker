from fastapi import FastAPI, Request


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Server is running"}


@app.post("/get_news")
async def get_news(request: Request):
    data = await request.json()

    api_id = data.get("api_id")
    api_hash = data.get("api_hash")
    password = data.get("Password")
    print(data)

    # Здесь пока просто выводим в ответ то, что пришло
    return {
        "api_id": api_id,
        "api_hash": api_hash,
        "password": password
    }

