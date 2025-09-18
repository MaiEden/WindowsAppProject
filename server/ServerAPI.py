# uvicorn ServerAPI:app --reload --port 8000
"""
Events Backend (Demo) – FastAPI routes.
queries are delegated to server.database.read_api;
commands are delegated to server.database.insert_api.
"""
from typing import Optional, Dict, Any, List
import server.database.read_api as read_api
from server.database import insert_api
from server.external_services.cordinats.geocoding_client import get_address
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Events Backend (Demo)")

# Allow all origins in demo mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/DB/users/get_user_by_name/{user_name}")
def get_user_by_user_name(user_name: str) -> Optional[Dict[str, Any]]:
    """Return a single user by username."""
    user = read_api.get_user_by_user_name(user_name)
    return user

@app.get("/DB/users/insert_user/{phone}/{username}/{password_hash}/{region}")
def insert_user(phone: str, username: str, password_hash: str, region: str) -> int:
    """Create a new user and return the inserted UserId."""
    return insert_api.add_user(phone, username, password_hash, region)

@app.get("/DB/decors/list")
async def get_decors():
    """List decor cards with no filters."""
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
    """
    List service cards with optional filters/sorting/paging.
    Query params mirror read_api.get_service_cards.
    """
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

@app.get("/DB/decors/get/{decor_id}")
def get_decor(decor_id: int):
    """Return a single decor item by DecorId."""
    return read_api.get_decor_by_id(decor_id)

@app.get("/DB/services/get/{service_id}")
def get_service(service_id: int):
    """Return a single service by ServiceId."""
    return read_api.get_service_by_id(service_id)

@app.get("/DB/halls/get/{hall_id}")
def get_hall(hall_id: int, resolveAddress: bool = True):
    """
    Return a single hall by HallId.
    If resolveAddress=True and hall has (Latitude, Longitude), add an 'Address' field
    using reverse geocoding; on failure, add 'AddressError' instead and still return the row.
    """
    row = read_api.get_hall_by_id(hall_id)
    if not row:
        return None
    if resolveAddress:
        lat = row.get("Latitude")
        lon = row.get("Longitude")
        if lat is not None and lon is not None:
            try:
                # Adds dict with fields such as 'formatted_address'
                row["Address"] = get_address(float(lat), float(lon))
            except Exception as e:
                # Do not fail the request solely because geocoding failed
                row["AddressError"] = str(e)
    return row

@app.get("/DB/users/{user_id}/decor/used")
def user_decor_used(user_id: int) -> List[Dict[str, Any]]:
    """List decor items linked to the user."""
    return read_api.get_decor_used_by_user(user_id)

@app.get("/DB/users/{user_id}/services/used")
def user_services_used(user_id: int) -> List[Dict[str, Any]]:
    """List services linked to the user."""
    return read_api.get_services_used_by_user(user_id)

@app.get("/DB/users/{user_id}/halls/used")
def user_halls_used(user_id: int) -> List[Dict[str, Any]]:
    """List halls linked to the user."""
    return read_api.get_halls_used_by_user(user_id)

@app.get("/DB/users/{user_id}/owned")
def user_owned_items(user_id: int) -> List[Dict[str, Any]]:
    """List all assets owned by the user (union of Hall/Service/Decor)."""
    return read_api.get_owned_items_by_user(user_id)

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
    """
    List decor items with S/M/L prices + computed MidPrice.
    Supports filters/sorting/paging (see read_api.get_decor_prices).
    """
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
    """
    List hall cards with optional filters (type, accessible, region, text),
    sorting, and paging (see read_api.get_hall_cards).
    """
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

from fastapi import Body

@app.post("/DB/decors/create")
def create_decor(
    decor_name: str = Body(..., alias="DecorName"),
    category: str = Body(..., alias="Category"),
    theme: Optional[str] = Body(None, alias="Theme"),
    description: Optional[str] = Body(None, alias="Description"),
    indoor: bool = Body(True, alias="Indoor"),
    requires_electricity: bool = Body(False, alias="RequiresElectricity"),
    price_small: Optional[float] = Body(None, alias="PriceSmall"),
    price_medium: Optional[float] = Body(None, alias="PriceMedium"),
    price_large: Optional[float] = Body(None, alias="PriceLarge"),
    delivery_fee: Optional[float] = Body(None, alias="DeliveryFee"),
    region: Optional[str] = Body(None, alias="Region"),
    vendor_name: Optional[str] = Body(None, alias="VendorName"),
    contact_phone: Optional[str] = Body(None, alias="ContactPhone"),
    contact_email: Optional[str] = Body(None, alias="ContactEmail"),
    photo_url: Optional[str] = Body(None, alias="PhotoUrl"),
    lead_time_days: Optional[int] = Body(None, alias="LeadTimeDays"),
    cancellation_policy: Optional[str] = Body(None, alias="CancellationPolicy"),
    available: bool = Body(True, alias="Available"),
) -> int:
    data = {
        "DecorName": decor_name,
        "Category": category,
        "Theme": theme,
        "Description": description,
        "Indoor": indoor,
        "RequiresElectricity": requires_electricity,
        "PriceSmall": price_small,
        "PriceMedium": price_medium,
        "PriceLarge": price_large,
        "DeliveryFee": delivery_fee,
        "Region": region,
        "VendorName": vendor_name,
        "ContactPhone": contact_phone,
        "ContactEmail": contact_email,
        "PhotoUrl": photo_url,
        "LeadTimeDays": lead_time_days,
        "CancellationPolicy": cancellation_policy,
        "Available": available,
    }
    return insert_api.add_decor_option(data)

@app.post("/DB/user_decor/link")
def link_user_decor(
    user_id: int = Body(..., alias="UserId"),
    decor_id: int = Body(..., alias="DecorId"),
    relation_type: str = Body("OWNER", alias="RelationType"),
) -> int:
    return insert_api.link_user_decor(user_id, decor_id, relation_type)
