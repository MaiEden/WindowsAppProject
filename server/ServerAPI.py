from typing import Optional, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from server.database.read_api import *
import server.database.read_api as read_api
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
    return read_api.get_events()

@app.get("/DB/users/get_user_by_id/{user_id}")
def get_user_by_user_name(user_name: str) -> Optional[Dict[str, Any]]:
    """החזרת משתמש לפי מזהה"""
    user = read_api.get_user_by_user_name(user_name)
    return user