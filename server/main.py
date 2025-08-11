# server/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"msg": "EasyEventPlaning backend is running!"}
