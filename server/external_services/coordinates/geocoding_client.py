# geocoding_client.py
# Thin client for reverse geocoding via Nominatim (OpenStreetMap).
# Provides both async and sync APIs with basic lat/lon validation and
# normalized Address output.
from __future__ import annotations
import asyncio
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from server.gateway.AsyncGateway import AsyncGateway
from server.gateway.gateway import Gateway

@dataclass
class Address:
    """
        Normalized address envelope returned from Nominatim
        use .as_json() to dict.
    """
    lat: float
    lon: float
    formatted_address: Optional[str]
    road: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postcode: Optional[str]
    country: Optional[str]
    display_name: Optional[str]
    source: str = "nominatim"

    def as_json(self) -> Dict[str, Any]:
        """Return the dataclass as a plain dict (for logging/serialization)."""
        return asdict(self)


def _validate_lat_lon(lat: float, lon: float) -> None:
    """
        Guard: lat ∈ [-90, 90], lon ∈ [-180, 180]
        raise ValueError on invalid input.
    """
    if not (-90.0 <= lat <= 90.0):
        raise ValueError("lat out of range (-90..90).")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError("lon out of range (-180..180).")


_async_gateway = AsyncGateway(timeout=12.0)


async def _reverse_geocode_async(lat: float, lon: float) -> Dict[str, Any]:
    """
        Async reverse-geocode against Nominatim
        returns Address as dict with smart fallbacks.
    """
    _validate_lat_lon(lat, lon)

    base = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": f"{lat:.8f}",
        "lon": f"{lon:.8f}",
        "format": "jsonv2",
        "accept-language": "en",
        "addressdetails": 1,
        "zoom": 18,
    }
    headers = {
        "User-Agent": "GeoClient/1.0 (contact: example@example.com)"
    }
    js = await _async_gateway.get(base, params=params, headers=headers)

    addr = js.get("address", {}) if isinstance(js, dict) else {}
    return Address(
        lat=lat,
        lon=lon,
        formatted_address=js.get("display_name"),
        road=addr.get("road") or addr.get("pedestrian") or addr.get("footway"),
        city=addr.get("city") or addr.get("town") or addr.get("village") or addr.get("hamlet"),
        state=addr.get("state"),
        postcode=addr.get("postcode"),
        country=addr.get("country"),
        display_name=js.get("name") or js.get("display_name"),
    ).as_json()


_sync_gateway = Gateway(timeout=10)


def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """
        Sync wrapper around the async call
        works with or without a running event loop.
    """
    try:
        return asyncio.run(_reverse_geocode_async(lat, lon))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_reverse_geocode_async(lat, lon))


def reverse_geocode_sync_via_requests(lat: float, lon: float) -> Dict[str, Any]:
    """
        Pure sync variant using Gateway.get (text) + json.loads
        returns Address dict.
    """
    _validate_lat_lon(lat, lon)
    base = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": f"{lat:.8f}",
        "lon": f"{lon:.8f}",
        "format": "jsonv2",
        "accept-language": "en",
        "addressdetails": 1,
        "zoom": 18,
    }
    headers = {
        "User-Agent": "GeoClient/1.0 (contact: example@example.com)"
    }
    text = _sync_gateway.get(base, params=params, headers=headers)
    if not text:
        raise ConnectionError("No response from Gateway.get")
    js = json.loads(text)
    addr = js.get("address", {}) if isinstance(js, dict) else {}
    return Address(
        lat=lat,
        lon=lon,
        formatted_address=js.get("display_name"),
        road=addr.get("road") or addr.get("pedestrian") or addr.get("footway"),
        city=addr.get("city") or addr.get("town") or addr.get("village") or addr.get("hamlet"),
        state=addr.get("state"),
        postcode=addr.get("postcode"),
        country=addr.get("country"),
        display_name=js.get("name") or js.get("display_name"),
    ).as_json()


async def get_address_async(lat: float, lon: float) -> Dict[str, Any]:
    """Public async alias for reverse geocoding (Address dict)."""
    return await _reverse_geocode_async(lat, lon)


def get_address(lat: float, lon: float) -> Dict[str, Any]:
    """Public sync alias for reverse geocoding (Address dict)."""
    return reverse_geocode(lat, lon)

