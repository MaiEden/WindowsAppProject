#uvicorn ServerAPI:app --reload --port 8000
from typing import Optional, Dict, Any, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import server.database.read_api as read_api
from server.database import insert_api
from server.external_services.cordinats.geocoding_client import get_address

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


# ServerAPI.py
@app.get("/DB/services/get/{service_id}")
def get_service(service_id: int):
    return read_api.get_service_by_id(service_id)


# --- Halls: get single + optional reverse geocode ---
@app.get("/DB/halls/get/{hall_id}")
def get_hall(hall_id: int, resolveAddress: bool = True):
    row = read_api.get_hall_by_id(hall_id)
    if not row:
        return None
    # אם יש קואורדינטות ונדרש גיאוקוד
    if resolveAddress:
        lat = row.get("Latitude")
        lon = row.get("Longitude")
        if lat is not None and lon is not None:
            try:
                row["Address"] = get_address(float(lat), float(lon))  # dict עם formatted_address ועוד
            except Exception as e:
                # לא להפיל את הבקשה רק בגלל גיאוקוד
                row["AddressError"] = str(e)
    return row

@app.get("/DB/users/{user_id}/decor/used")
def user_decor_used(user_id: int) -> List[Dict[str, Any]]:
    return read_api.get_decor_used_by_user(user_id)

@app.get("/DB/users/{user_id}/services/used")
def user_services_used(user_id: int) -> List[Dict[str, Any]]:
    return read_api.get_services_used_by_user(user_id)

@app.get("/DB/users/{user_id}/halls/used")
def user_halls_used(user_id: int) -> List[Dict[str, Any]]:
    return read_api.get_halls_used_by_user(user_id)

@app.get("/DB/users/{user_id}/owned")
def user_owned_items(user_id: int) -> List[Dict[str, Any]]:
    return read_api.get_owned_items_by_user(user_id)

# --- NEW: Decor prices endpoint with computed MidPrice ---
@app.get("/DB/decors/prices")
def list_decor_prices(
        search: Optional[str] = None,
        category: Optional[str] = None,
        available: Optional[bool] = None,
        region: Optional[str] = None,
        order_by: str = "MidPrice",
        ascending: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
):
    return read_api.get_decor_prices(
        search=search,
        category=category,
        available=available,
        region=region,
        order_by=order_by,
        ascending=ascending,
        limit=limit,
        offset=offset,
    )
#uvicorn ServerAPI:app --reload --port 8000
from typing import Optional, Dict, Any, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import server.database.read_api as read_api
from server.database import insert_api
from server.external_services.cordinats.geocoding_client import get_address

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


# ServerAPI.py
@app.get("/DB/services/get/{service_id}")
def get_service(service_id: int):
    return read_api.get_service_by_id(service_id)


# --- Halls: get single + optional reverse geocode ---
@app.get("/DB/halls/get/{hall_id}")
def get_hall(hall_id: int, resolveAddress: bool = True):
    row = read_api.get_hall_by_id(hall_id)
    if not row:
        return None
    # אם יש קואורדינטות ונדרש גיאוקוד
    if resolveAddress:
        lat = row.get("Latitude")
        lon = row.get("Longitude")
        if lat is not None and lon is not None:
            try:
                row["Address"] = get_address(float(lat), float(lon))  # dict עם formatted_address ועוד
            except Exception as e:
                # לא להפיל את הבקשה רק בגלל גיאוקוד
                row["AddressError"] = str(e)
    return row

@app.get("/DB/users/{user_id}/decor/used")
def user_decor_used(user_id: int) -> List[Dict[str, Any]]:
    return read_api.get_decor_used_by_user(user_id)

@app.get("/DB/users/{user_id}/services/used")
def user_services_used(user_id: int) -> List[Dict[str, Any]]:
    return read_api.get_services_used_by_user(user_id)

@app.get("/DB/users/{user_id}/halls/used")
def user_halls_used(user_id: int) -> List[Dict[str, Any]]:
    return read_api.get_halls_used_by_user(user_id)

@app.get("/DB/users/{user_id}/owned")
def user_owned_items(user_id: int) -> List[Dict[str, Any]]:
    return read_api.get_owned_items_by_user(user_id)

# --- NEW: Decor prices endpoint with computed MidPrice ---
@app.get("/DB/decors/prices")
def list_decor_prices(
        search: Optional[str] = None,
        category: Optional[str] = None,
        available: Optional[bool] = None,
        region: Optional[str] = None,
        order_by: str = "MidPrice",
        ascending: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
):
    return read_api.get_decor_prices(
        search=search,
        category=category,
        available=available,
        region=region,
        order_by=order_by,
        ascending=ascending,
        limit=limit,
        offset=offset,
    )

# ---------- User <-> Decor link ----------
class UserDecorLink(BaseModel):
    UserId: int
    DecorId: int
    RelationType: str = "OWNER"  # 'OWNER' or 'USER'


@app.post("/DB/user_decor/link")
def link_user_decor(link: UserDecorLink) -> int:
    """
    Creates a UserDecor relation row.
    """
    from server.database import insert_api
    return insert_api.link_user_decor(link.UserId, link.DecorId, link.RelationType)
