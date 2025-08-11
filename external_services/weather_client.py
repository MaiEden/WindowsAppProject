from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import asyncio

import httpx
from pydantic import BaseModel

# =========================
#   Exceptions & Constants
# =========================


class UnsupportedDateError(ValueError):
    """Raised when the requested datetime is outside supported forecast/archive ranges."""


# Open-Meteo limits (practical)
FORECAST_MAX_FWD_DAYS = 16             # forecast horizon ~16 days ahead
ARCHIVE_EARLIEST_UTC = datetime(1940, 1, 1, tzinfo=timezone.utc)  # safe lower bound
ARCHIVE_LATEST_DELAY_DAYS = 5          # archive latency for very recent past

# =========================
#   Data Model
# =========================

class Weather(BaseModel):
    time_utc: str
    temperature_c: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    precipitation_mm: Optional[float] = None
    precipitation_probability_percent: Optional[float] = None
    source: str  # "open-meteo-forecast" / "open-meteo-archive"

    def as_json(self) -> Dict[str, Any]:
        return self.model_dump()

# =========================
#   Time Parsing & Validation
# =========================

def parse_iso_to_utc(dt: str) -> datetime:
    """
    Parse ISO-8601 datetime string WITH timezone into a UTC datetime aligned to top-of-hour.
    Examples:
      2025-08-11T17:00:00+03:00
      2025-08-11T14:00:00Z
    """
    s = dt.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        d = datetime.fromisoformat(s)
    except ValueError as e:
        raise ValueError(
            f"Bad datetime. Use ISO-8601 with timezone, e.g. 2025-08-11T17:00:00+03:00 ({e})"
        )
    if d.tzinfo is None:
        raise ValueError("Datetime must include timezone offset (e.g. +03:00 or Z).")

    # work on exact hours
    return d.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def validate_supported_datetime(dt_utc: datetime, now_utc: datetime) -> None:
    """
    Ensure the requested datetime is within supported ranges.
    Raises UnsupportedDateError with a clear message if not.
    """
    # Too far in the future for forecast
    if dt_utc > now_utc + timedelta(days=FORECAST_MAX_FWD_DAYS):
        raise UnsupportedDateError(
            f"Requested datetime {dt_utc.isoformat()} is beyond the forecast horizon "
            f"({FORECAST_MAX_FWD_DAYS} days). Choose an earlier date/time or use a long-range provider."
        )

    # Too far in the past for our archive bounds
    if dt_utc < ARCHIVE_EARLIEST_UTC:
        raise UnsupportedDateError(
            f"Requested datetime {dt_utc.isoformat()} is earlier than supported archive start "
            f"({ARCHIVE_EARLIEST_UTC.date()})."
        )

    # Very recent past (archive latency window)
    # We cover last 2 days using forecast (with past_days=2). Between 2..5 days back, archive may not be ready yet.
    if (now_utc - timedelta(days=ARCHIVE_LATEST_DELAY_DAYS)) < dt_utc <= (now_utc - timedelta(days=2)):
        raise UnsupportedDateError(
            "Historical data for very recent days may be unavailable yet. "
            "Pick a time at least 5 days before today, or within the last 2 days (covered by forecast with past_days)."
        )

# =========================
#   Open-Meteo Calls
# =========================


async def fetch_open_meteo_forecast(lat: float, lon: float, dt_utc: datetime) -> Weather:
    """
    Fetch a single hour from Open-Meteo forecast endpoint using start_hour=end_hour.
    """
    base = "https://api.open-meteo.com/v1/forecast"
    hour = dt_utc.strftime("%Y-%m-%dT%H:00")
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m,precipitation,precipitation_probability",
        "timezone": "GMT",
        "timeformat": "iso8601",
        "start_hour": hour,
        "end_hour": hour,
        # Stable units
        "windspeed_unit": "kmh",
        "precipitation_unit": "mm",
        "temperature_unit": "celsius",
        # Ensure we can reach up to 48h back via forecast
        "past_days": 2,
    }
    async with httpx.AsyncClient(timeout=12) as client:
        r = await client.get(base, params=params)
        r.raise_for_status()
        js = r.json()

    h = js.get("hourly", {})
    times = h.get("time", [])
    if not times:
        raise LookupError("No forecast data for requested hour (outside forecast horizon?)")

    return Weather(
        time_utc=times[0],
        temperature_c=(h.get("temperature_2m") or [None])[0],
        wind_speed_kmh=(h.get("wind_speed_10m") or [None])[0],
        precipitation_mm=(h.get("precipitation") or [None])[0],
        precipitation_probability_percent=(h.get("precipitation_probability") or [None])[0],
        source="open-meteo-forecast",
    )


async def fetch_open_meteo_archive(lat: float, lon: float, dt_utc: datetime) -> Weather:
    """
    Fetch a single hour from Open-Meteo archive endpoint (request full day, pick the hour).
    """
    base = "https://archive-api.open-meteo.com/v1/archive"
    day = dt_utc.strftime("%Y-%m-%d")
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": day,
        "end_date": day,
        "hourly": "temperature_2m,wind_speed_10m,precipitation",
        "timezone": "GMT",
        "timeformat": "iso8601",
        "windspeed_unit": "kmh",
        "precipitation_unit": "mm",
        "temperature_unit": "celsius",
    }
    async with httpx.AsyncClient(timeout=12) as client:
        r = await client.get(base, params=params)
        r.raise_for_status()
        js = r.json()

    h = js.get("hourly", {})
    times = h.get("time", [])
    if not times:
        raise LookupError("No historical data returned (dataset delay or out of range).")

    target = dt_utc.strftime("%Y-%m-%dT%H:00")
    try:
        i = times.index(target)
    except ValueError:
        raise LookupError(f"Hour {target} not found in archive for that day.")

    return Weather(
        time_utc=times[i],
        temperature_c=(h.get("temperature_2m") or [None])[i],
        wind_speed_kmh=(h.get("wind_speed_10m") or [None])[i],
        precipitation_mm=(h.get("precipitation") or [None])[i],
        precipitation_probability_percent=None,  # archive lacks hourly PoP
        source="open-meteo-archive",
    )

# =========================
#   Public API (async & sync)
# =========================


async def _get_weather_async(lat: float, lon: float, datetime_iso: str) -> Dict[str, Any]:
    """
    Core async function: validates inputs, routes to forecast/archive and returns a JSON dict.
    """
    # basic lat/lon validation
    if not (-90.0 <= lat <= 90.0):
        raise ValueError("lat out of range (-90..90).")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError("lon out of range (-180..180).")

    dt_utc = parse_iso_to_utc(datetime_iso)
    now = datetime.now(timezone.utc)

    # upfront range validation
    validate_supported_datetime(dt_utc, now)

    # route: within -2..+16 days -> forecast; else -> archive
    if (now - timedelta(days=2)) <= dt_utc <= (now + timedelta(days=FORECAST_MAX_FWD_DAYS)):
        w = await fetch_open_meteo_forecast(lat, lon, dt_utc)
        return w.as_json()
    else:
        w = await fetch_open_meteo_archive(lat, lon, dt_utc)
        return w.as_json()


def get_weather(lat: float, lon: float, datetime_iso: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for convenient use from any Python code.

    Returns a dict with:
      time_utc, temperature_c, wind_speed_kmh, precipitation_mm,
      precipitation_probability_percent, source.

    Raises:
      ValueError / UnsupportedDateError / LookupError / httpx.HTTPError
    """
    try:
        return asyncio.run(_get_weather_async(lat, lon, datetime_iso))
    except RuntimeError:
        # If already inside a running event loop (e.g., some GUI/async environments)
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_get_weather_async(lat, lon, datetime_iso))
