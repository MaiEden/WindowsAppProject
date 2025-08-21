"""
read_api.py
Read-only API to fetch data and aggregated reports from the Events app schema.

This module provides:
-------------------------
- get_users():            Basic list of users.
- get_halls():            Halls catalog.
- get_events():           Events with the manager (user) name.
- get_user_services():    Flat mapping of which services each user offers.
- report_users_with_services_and_events():
                         Per-user aggregation: offered services + events managed.
- report_events_with_services_and_manager():
                         Per-event aggregation: manager + services planned.
"""

import pyodbc
from typing import List, Dict, Any, Optional, Sequence
from decimal import Decimal
from server.gateway.DBgateway import DbGateway

db = DbGateway()


def _fetchall_dicts(cur: pyodbc.Cursor) -> List[Dict[str, Any]]:
    """
    Convert the current cursor resultset into a list of dictionaries.
    """
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def print_table(
        rows: Sequence[Dict[str, Any]],
        columns: Optional[Sequence[str]] = None,
        max_col_width: int = 30,
) -> None:
    """
    Pretty-print a list of dictionaries as a fixed-width table.
    """
    if not rows:
        print("(no rows)")
        return

    if columns is None:
        seen = []
        for r in rows:
            for k in r.keys():
                if k not in seen:
                    seen.append(k)
        columns = seen

    def fmt(val: Any) -> str:
        s = "" if val is None else str(val)
        if max_col_width and len(s) > max_col_width:
            return s[: max_col_width - 1] + "…"
        return s

    widths = []
    for col in columns:
        col_width = len(str(col))
        for r in rows:
            col_width = max(col_width, len(fmt(r.get(col))))
        widths.append(col_width)

    def is_number(v: Any) -> bool:
        return isinstance(v, (int, float, Decimal))

    def cell(val: Any, w: int) -> str:
        text = fmt(val)
        return text.rjust(w) if is_number(val) else text.ljust(w)

    header = " | ".join(str(col).ljust(w) for col, w in zip(columns, widths))
    sep = "-+-".join("-" * w for w in widths)
    print(header)
    print(sep)

    for r in rows:
        line = " | ".join(cell(r.get(col), w) for col, w in zip(columns, widths))
        print(line)


def get_users() -> List[Dict[str, Any]]:
    sql = "SELECT * FROM dbo.Users ORDER BY Username;"
    return db.query(sql)


def get_halls() -> List[Dict[str, Any]]:
    """
    Fetch all hall details.

    Returns list of dicts:
    [{HallId, HallName, HallType, Capacity, Region,
      Latitude, Longitude, Description, PricePerHour, PricePerDay, PricePerPerson,
      ParkingAvailable, WheelchairAccessible, ContactPhone, ContactEmail, WebsiteUrl, PhotoUrl}, ...]
    """
    sql = """
    SELECT
        h.HallId,
        h.HallName,
        h.HallType,
        h.Capacity,
        h.Region,
        h.Latitude,
        h.Longitude,
        h.Description,
        h.PricePerHour,
        h.PricePerDay,
        h.PricePerPerson,
        h.ParkingAvailable,
        h.WheelchairAccessible,
        h.ContactPhone,
        h.ContactEmail,
        h.WebsiteUrl,
        h.PhotoUrl
    FROM dbo.Hall h
    ORDER BY h.HallName;
    """
    return db.query(sql)

def get_halls_filtered(
        region: Optional[str] = None,
        hall_type: Optional[str] = None,
        search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch halls with optional filters for region, type, and search by name/description.
    """
    sql = """
    SELECT
        h.HallId,
        h.HallName,
        h.HallType,
        h.Capacity,
        h.Region,
        h.Latitude,
        h.Longitude,
        h.Description,
        h.PricePerHour,
        h.PricePerDay,
        h.PricePerPerson,
        h.ParkingAvailable,
        h.WheelchairAccessible,
        h.ContactPhone,
        h.ContactEmail,
        h.WebsiteUrl,
        h.PhotoUrl
    FROM dbo.Hall h
    WHERE 1=1
    """
    params = []

    if region and region != "All regions":
        sql += " AND h.Region = ?"
        params.append(region)

    if hall_type and hall_type != "All types":
        sql += " AND h.HallType = ?"
        params.append(hall_type)

    if search:
        sql += " AND (h.HallName LIKE ? OR h.Description LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like])

    sql += " ORDER BY h.HallName;"

    return db.query(sql, params)


def get_events() -> List[Dict[str, Any]]:
    sql = """
    SELECT e.EventId,
           e.EventDate,
           CONVERT(NVARCHAR(8), e.EventTime, 108) AS EventTime,
           e.EventType,
           u.Username AS Manager
    FROM dbo.Event e
    INNER JOIN dbo.Users u ON u.UserId = e.ManagerUserId
    ORDER BY e.EventDate, e.EventTime;
    """
    return db.query(sql)


def get_user_services() -> List[Dict[str, Any]]:
    """
    Flat mapping of which services each user offers.
    """
    sql = """
    SELECT u.Username, us.ServiceType, us.ServiceKey
    FROM dbo.UserService us
    INNER JOIN dbo.Users u ON u.UserId = us.UserId
    ORDER BY u.Username, us.ServiceType;
    """
    return db.query(sql)


def report_users_with_services_and_events() -> List[Dict[str, Any]]:
    sql = """
    SELECT
        u.UserId,
        u.Username,
        u.Phone,
        u.Region,
        ISNULL((
            SELECT STRING_AGG(d.ServiceType, ', ')
            FROM (
                SELECT DISTINCT us2.ServiceType
                FROM dbo.UserService us2
                WHERE us2.UserId = u.UserId
            ) d
        ), 'None') AS ServicesOffered,
        ISNULL((
            SELECT STRING_AGG(d.EventLabel, ' | ')
            FROM (
                SELECT DISTINCT CONVERT(NVARCHAR(30), e.EventDate) + ' ' + e.EventType AS EventLabel
                FROM dbo.Event e
                WHERE e.ManagerUserId = u.UserId
            ) d
        ), 'None') AS EventsManaged
    FROM dbo.Users u
    ORDER BY u.Username;
    """
    return db.query(sql)


def report_events_with_services_and_manager() -> List[Dict[str, Any]]:
    sql = """
    SELECT
        e.EventId,
        CONVERT(NVARCHAR(30), e.EventDate) AS EventDate,
        CONVERT(NVARCHAR(8), e.EventTime, 108) AS EventTime,
        e.EventType,
        u.Username AS Manager,
        ISNULL((
            SELECT STRING_AGG(d.ServiceType, ', ')
            FROM (
                SELECT DISTINCT es.ServiceType
                FROM dbo.EventService es
                WHERE es.EventId = e.EventId
            ) d
        ), 'None') AS Services
    FROM dbo.Event e
    INNER JOIN dbo.Users u ON u.UserId = e.ManagerUserId
    ORDER BY e.EventDate, e.EventTime;
    """
    return db.query(sql)


def report_halls_with_region() -> List[Dict[str, Any]]:
    sql = """
    SELECT
        h.HallName,
        h.HallType,
        h.Region,
        h.Capacity,
        h.PricePerPerson,
        h.PricePerHour,
        h.PricePerDay
    FROM dbo.Hall h
    ORDER BY h.Region, h.HallName;
    """
    return db.query(sql)


def get_user_by_user_name(user_name: str) -> Optional[Dict[str, Any]]:
    sql = "SELECT * FROM dbo.Users WHERE Username = ?;"
    results = db.query(sql, (user_name,))
    return results[0] if results else None


if __name__ == "__main__":
    print(get_user_by_user_name("Noa Hadad"))
    print("Users:"); print_table(get_users())
    print("\nEvents:"); print_table(get_events())
    print("\nUserServices:"); print_table(get_user_services())
    print("\nReport: Users with services & events"); print_table(report_users_with_services_and_events())
    print("\nReport: Events with services & manager"); print_table(report_events_with_services_and_manager())
    print("\nHalls:"); print_table(get_halls())
    print("\nReport: Halls with region"); print_table(report_halls_with_region())
