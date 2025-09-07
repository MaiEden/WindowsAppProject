"""
read_api.py
Read-only API to fetch data and aggregated reports from the Events app schema.

This module provides:
-------------------------
- get_users():   Return list of all users.
- get_halls():   Full catalog of halls.
- get_halls_filtered(): Filter halls by region, type, and search text.
- get_events():  Events with manager username.
- get_user_services(): Mapping of services offered by each user.
- report_users_with_services_and_events(): Per-user aggregation.
- report_events_with_services_and_manager(): Per-event aggregation.
- report_halls_with_region(): Halls grouped by region.
- get_user_by_user_name(): Lookup of a single user.

Additionally:
- _fetchall_dicts(): Converts pyodbc cursor results to list of dicts.
- print_table(): Helper for pretty-printing rows in tabular format.
"""

import pyodbc
from typing import List, Dict, Any, Optional, Sequence
from decimal import Decimal
from server.gateway.DBgateway import DbGateway

db = DbGateway()


def _fetchall_dicts(cur: pyodbc.Cursor) -> List[Dict[str, Any]]:
    """
    Convert a pyodbc cursor into a list of dictionaries.
    Each dict maps {column_name: value}.
    """
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def print_table(
        rows: Sequence[Dict[str, Any]],
        columns: Optional[Sequence[str]] = None,
        max_col_width: int = 100,
) -> None:
    """
    Pretty-print a list of dictionaries as a text table.

    Args:
        rows: list of dict rows.
        columns: optional explicit list of columns; if None, infer from data.
        max_col_width: truncate long values to this width.
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
    """Fetch all users ordered by username."""
    sql = "SELECT * FROM dbo.Users ORDER BY Username;"
    return db.query(sql)


def get_halls() -> List[Dict[str, Any]]:
    """
    Fetch all hall details.
    Returns a list of dictionaries with hall metadata.
    """
    sql = """
    SELECT
        h.HallId, h.HallName, h.HallType, h.Capacity, h.Region,
        h.Latitude, h.Longitude, h.Description,
        h.PricePerHour, h.PricePerDay, h.PricePerPerson,
        h.ParkingAvailable, h.WheelchairAccessible,
        h.ContactPhone, h.ContactEmail, h.WebsiteUrl, h.PhotoUrl
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
    Fetch halls with optional filters for region, type, and free-text search
    across name/description.
    """
    sql = """
    SELECT
        h.HallId, h.HallName, h.HallType, h.Capacity, h.Region,
        h.Latitude, h.Longitude, h.Description,
        h.PricePerHour, h.PricePerDay, h.PricePerPerson,
        h.ParkingAvailable, h.WheelchairAccessible,
        h.ContactPhone, h.ContactEmail, h.WebsiteUrl, h.PhotoUrl
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
    """Fetch all events with manager username."""
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
    """Return mapping of services offered by each user."""
    sql = """
    SELECT u.Username, us.ServiceType, us.ServiceKey
    FROM dbo.UserService us
    INNER JOIN dbo.Users u ON u.UserId = us.UserId
    ORDER BY u.Username, us.ServiceType;
    """
    return db.query(sql)


def report_users_with_services_and_events() -> List[Dict[str, Any]]:
    """
    Aggregated report:
    For each user show region, services offered, and events managed.
    """
    sql = """
    SELECT
        u.UserId, u.Username, u.Phone, u.Region,
        ISNULL((SELECT STRING_AGG(d.ServiceType, ', ')
                FROM (SELECT DISTINCT us2.ServiceType
                      FROM dbo.UserService us2
                      WHERE us2.UserId = u.UserId) d),
               'None') AS ServicesOffered,
        ISNULL((SELECT STRING_AGG(d.EventLabel, ' | ')
                FROM (SELECT DISTINCT CONVERT(NVARCHAR(30), e.EventDate) + ' ' + e.EventType AS EventLabel
                      FROM dbo.Event e
                      WHERE e.ManagerUserId = u.UserId) d),
               'None') AS EventsManaged
    FROM dbo.Users u
    ORDER BY u.Username;
    """
    return db.query(sql)


def report_events_with_services_and_manager() -> List[Dict[str, Any]]:
    """
    Aggregated report:
    For each event show manager username and list of services attached.
    """
    sql = """
    SELECT
        e.EventId,
        CONVERT(NVARCHAR(30), e.EventDate) AS EventDate,
        CONVERT(NVARCHAR(8), e.EventTime, 108) AS EventTime,
        e.EventType,
        u.Username AS Manager,
        ISNULL((SELECT STRING_AGG(d.ServiceType, ', ')
                FROM (SELECT DISTINCT es.ServiceType
                      FROM dbo.EventService es
                      WHERE es.EventId = e.EventId) d),
               'None') AS Services
    FROM dbo.Event e
    INNER JOIN dbo.Users u ON u.UserId = e.ManagerUserId
    ORDER BY e.EventDate, e.EventTime;
    """
    return db.query(sql)


def report_halls_with_region() -> List[Dict[str, Any]]:
    """List halls by region, including capacity and pricing."""
    sql = """
    SELECT h.HallName, h.HallType, h.Region,
           h.Capacity, h.PricePerPerson, h.PricePerHour, h.PricePerDay
    FROM dbo.Hall h
    ORDER BY h.Region, h.HallName;
    """
    return db.query(sql)


def get_user_by_user_name(user_name: str) -> Optional[Dict[str, Any]]:
    """Lookup a single user by username."""
    sql = "SELECT * FROM dbo.Users WHERE Username = ?;"
    results = db.query(sql, (user_name,))
    return results[0] if results else None

def get_tables_name():
    sql = "SELECT name FROM sys.tables"
    return db.query(sql)

def get_decotators():
    sql = "SELECT * FROM dbo.DecorOption"
    return db.query(sql)

def get_decor_cards(
    search: Optional[str] = None,
    category: Optional[str] = None,
    available: Optional[bool] = None,
    region: Optional[str] = None,
    order_by: str = "DecorName",     # DecorName | MinPrice | Region | Category
    ascending: bool = True,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Return a slim list of decor items for cards, with optional filters & paging.

    Filters:
      - search: free-text over DecorName, Description, Theme
      - category: exact match (ignore if 'All'/'')
      - available: True/False (None to ignore)
      - region: exact match (ignore if 'All'/'')
    Sorting:
      - order_by in {'DecorName','MinPrice','Region','Category'}
      - ascending True/False
    Paging:
      - if limit provided, uses OFFSET/FETCH (SQL Server 2012+)
    """

    # allowlisted ordering only (to avoid SQL injection)
    order_map = {
        "DecorName": "d.DecorName",
        "MinPrice":  "mp.MinPrice",
        "Region":    "d.Region",
        "Category":  "d.Category",
    }
    order_col = order_map.get(order_by, "d.DecorName")
    order_dir = "ASC" if ascending else "DESC"

    sql = f"""
    SELECT
        d.DecorId,
        d.DecorName,
        d.Category,
        d.Theme,
        d.Region,
        d.Available,
        d.PhotoUrl,
        mp.MinPrice
    FROM dbo.DecorOption AS d
    OUTER APPLY (
        SELECT MIN(v.p) AS MinPrice
        FROM (VALUES (d.PriceSmall), (d.PriceMedium), (d.PriceLarge)) AS v(p)
        WHERE v.p IS NOT NULL
    ) AS mp
    WHERE 1=1
    """
    params: List[Any] = []

    # Filters
    if category and category not in ("All", "All categories", ""):
        sql += " AND d.Category = ?"
        params.append(category)

    if region and region not in ("All", "All regions", ""):
        sql += " AND d.Region = ?"
        params.append(region)

    if available is True:
        sql += " AND d.Available = 1"
    elif available is False:
        sql += " AND d.Available = 0"

    if search:
        like = f"%{search}%"
        sql += " AND (d.DecorName LIKE ? OR d.Description LIKE ? OR d.Theme LIKE ?)"
        params.extend([like, like, like])

    # Ordering
    sql += f" ORDER BY {order_col} {order_dir}"

    # Paging
    if limit is not None:
        off = int(offset or 0)
        lim = int(limit)
        sql += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([off, lim])

    return db.query(sql, params)

def get_services():
    sql = "SELECT * FROM dbo.ServiceOption"
    return db.query(sql)

if __name__ == "__main__":
    print("services:"); print_table(get_services())
    # Demo printing of queries
    print(get_decor_cards())
    print("decorators:"); print_table(get_decotators())
    print(get_user_by_user_name("Noa Hadad"))
    print("Users:"); print_table(get_users())
    print("\nEvents:"); print_table(get_events())
    print("\nUserServices:"); print_table(get_user_services())
    print("\nReport: Users with services & events"); print_table(report_users_with_services_and_events())
    print("\nReport: Events with services & manager"); print_table(report_events_with_services_and_manager())
    print("\nHalls:"); print_table(get_halls())
    print("\nReport: Halls with region"); print_table(report_halls_with_region())
    print("\nTables:"); print_table(get_tables_name())
