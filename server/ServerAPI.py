#uvicorn ServerAPI:app --reload --port 8000
from typing import Optional, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import server.database.read_api as read_api
from server.database import insert_api

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

@app.get("/DB/users/get_user_by_name/{user_name}")
def get_user_by_user_name(user_name: str) -> Optional[Dict[str, Any]]:
    """החזרת משתמש לפי מזהה"""
    user = read_api.get_user_by_user_name(user_name)
    return user

@app.get("/DB/users/insert_user/{phone}/{username}/{password_hash}/{region}")
def insert_user(phone: str, username: str, password_hash: str, region: str) -> int:
    """הוספת משתמש חדש"""
    return insert_api.add_user(phone, username, password_hash, region)

@app.get("/DB/decors/list")
async def get_halls():
    """החזרת כל האולמות (דוגמה)"""
    return read_api.get_decor_cards()

@app.get("/DB/services/list")
def list_services(
    search: Optional[str] = None,
    category: Optional[str] = None,
    available: Optional[bool] = None,
    region: Optional[str] = None,
    order_by: str = "ServiceName",
    ascending: bool = True,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    return read_api.get_service_cards(
        search=search,
        category=category,
        available=available,
        region=region,
        order_by=order_by,
        ascending=ascending,
        limit=limit,
        offset=offset,
    )

@app.get("/DB/halls/list")
def list_halls(
    search: Optional[str] = None,
    hall_type: Optional[str] = None,
    accessible: Optional[bool] = None,
    region: Optional[str] = None,
    order_by: str = "HallName",
    ascending: bool = True,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
):
    return read_api.get_hall_cards(
        search=search,
        hall_type=hall_type,
        accessible=accessible,
        region=region,
        order_by=order_by,
        ascending=ascending,
        limit=limit,
        offset=offset,
    )

@app.get("/DB/decors/get/{decor_id}")
def get_decor(decor_id: int):
    return read_api.get_decor_by_id(decor_id)
