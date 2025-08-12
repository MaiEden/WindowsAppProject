from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.database.read_api import *
app = FastAPI(title="Events Backend (Demo)")

# מאפשר קריאות מכל מקור (בדמו)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Halls endpoint ---
@app.get("/DB/halls/get_halls")
async def get_halls():
    """החזרת כל האולמות (דוגמה)"""
    return get_events()