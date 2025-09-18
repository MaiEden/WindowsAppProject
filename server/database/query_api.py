"""
query_api.py - API to fetch data. (queries)

This module provides:
-------------------------
Users:
- get_users():                Return list of all users.
- get_user_by_user_name():    Lookup of a single user by username.

Halls:
- get_halls():                Full catalog of halls.
- get_hall_by_id():           Lookup of a single hall by ID.
- get_hall_cards():           Return hall cards with filters, sorting & paging.
- get_halls_used_by_user():   Halls used by a given user.

Services:
- get_services():             Full catalog of services.
- get_service_by_id():        Lookup of a single service by ID.
- get_service_cards():        Return service cards with filters, sorting & paging.
- get_services_used_by_user(): Services used by a given user.

Decor:
- get_decotators():           Full catalog of decor options.
- get_decor_by_id():          Lookup of a single decor item by ID.
- get_decor_cards():          Return decor cards with filters, sorting & paging.
- get_decor_prices():         Return decor items with S/M/L prices and MidPrice.
- get_decor_used_by_user():   Decor items used by a given user.

User ownership:
- get_owned_items_by_user():  All assets owned by a given user (union of hall/service/decor).

DB:
- get_tables_name():          Return all tables names.

Utilities:
- _fetchall_dicts():          Convert pyodbc cursor results to list of dicts.
- print_table():              Pretty-print rows in tabular format.
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

def get_user_by_user_name(user_name: str) -> Optional[Dict[str, Any]]:
    """Lookup a single user by username."""
    sql = "SELECT * FROM dbo.Users WHERE Username = ?;"
    results = db.query(sql, (user_name,))
    return results[0] if results else None

def get_decorators():
    """ Fetch all decorators. """
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
      - if limit provided, uses OFFSET/FETCH
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
    """ Fetch all services. """
    sql = "SELECT * FROM dbo.ServiceOption"
    return db.query(sql)

def get_service_cards(
    search: Optional[str] = None,
    category: Optional[str] = None,
    available: Optional[bool] = None,
    region: Optional[str] = None,
    order_by: str = "ServiceName",   # ServiceName | BasePrice | Region | Category
    ascending: bool = True,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Return a slim list of services for cards, with optional filters & paging.

    Filters:
      - search: free-text over ServiceName, Description, ShortDescription, Subcategory
      - category: exact match (ignore if 'All'/'')
      - available: True/False (None to ignore)
      - region: exact match (ignore if 'All'/'')
    Sorting:
      - order_by in {'ServiceName','BasePrice','Region','Category'}
      - ascending True/False
    Paging:
      - if limit provided, uses OFFSET/FETCH (SQL Server 2012+)
    """
    # allowlisted ordering only (to avoid SQL injection)
    order_map = {
        "ServiceName": "s.ServiceName",
        "BasePrice":   "s.BasePrice",
        "Region":      "s.Region",
        "Category":    "s.Category",
    }
    order_col = order_map.get(order_by, "s.ServiceName")
    order_dir = "ASC" if ascending else "DESC"

    sql = f"""
    SELECT
        s.ServiceId,
        s.ServiceName,
        s.Category,
        s.Subcategory,
        s.ShortDescription,
        s.Description,
        s.PhotoUrl,
        s.Region,
        s.Available,
        s.BasePrice,
        s.PricePerPerson
    FROM dbo.ServiceOption AS s
    WHERE 1=1
    """
    params: List[Any] = []

    # Filters
    if category and category not in ("All", "All categories", ""):
        sql += " AND s.Category = ?"
        params.append(category)

    if region and region not in ("All", "All regions", ""):
        sql += " AND s.Region = ?"
        params.append(region)

    if available is True:
        sql += " AND s.Available = 1"
    elif available is False:
        sql += " AND s.Available = 0"

    if search:
        like = f"%{search}%"
        sql += """
        AND (
            s.ServiceName LIKE ?
            OR s.Description LIKE ?
            OR s.ShortDescription LIKE ?
            OR s.Subcategory LIKE ?
        )
        """
        params.extend([like, like, like, like])

    # Ordering
    sql += f" ORDER BY {order_col} {order_dir}"

    # Paging
    if limit is not None:
        off = int(offset or 0)
        lim = int(limit)
        sql += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([off, lim])

    return db.query(sql, params)

def get_hall_cards(
    search: Optional[str] = None,
    hall_type: Optional[str] = None,
    accessible: Optional[bool] = None,
    region: Optional[str] = None,
    order_by: str = "HallName",   # HallName | Capacity | Region | HallType | MinPrice
    ascending: bool = True,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Return a slim list of halls for cards, with optional filters & paging.

    Filters:
      - search: free-text over HallName, Description
      - hall_type: exact match (ignore if 'All'/'')
      - accessible: True/False (filters by WheelchairAccessible)
      - region: exact match (ignore if 'All'/'')
    Sorting:
      - order_by in {'HallName','Capacity','Region','HallType','MinPrice'}
      - ascending True/False
    Paging:
      - if limit provided, uses OFFSET/FETCH (SQL Server 2012+)
    """

    order_map = {
        "HallName": "h.HallName",
        "Capacity": "h.Capacity",
        "Region": "h.Region",
        "HallType": "h.HallType",
        "MinPrice": "mp.MinPrice",
    }
    order_col = order_map.get(order_by, "h.HallName")
    order_dir = "ASC" if ascending else "DESC"

    sql = f"""
    SELECT
        h.HallId,
        h.HallName,
        h.HallType,
        h.Capacity,
        h.Region,
        h.WheelchairAccessible,
        h.PhotoUrl,
        mp.MinPrice
    FROM dbo.Hall AS h
    OUTER APPLY (
        SELECT MIN(v.p) AS MinPrice
        FROM (VALUES (h.PricePerPerson), (h.PricePerHour), (h.PricePerDay)) AS v(p)
        WHERE v.p IS NOT NULL
    ) AS mp
    WHERE 1=1
    """
    params: List[Any] = []

    # Filters
    if hall_type and hall_type not in ("All", "All types", ""):
        sql += " AND h.HallType = ?"
        params.append(hall_type)

    if region and region not in ("All", "All regions", ""):
        sql += " AND h.Region = ?"
        params.append(region)

    if accessible is True:
        sql += " AND h.WheelchairAccessible = 1"
    elif accessible is False:
        sql += " AND h.WheelchairAccessible = 0"

    if search:
        like = f"%{search}%"
        sql += " AND (h.HallName LIKE ? OR h.Description LIKE ?)"
        params.extend([like, like])

    # Ordering
    sql += f" ORDER BY {order_col} {order_dir}"

    # Paging
    if limit is not None:
        off = int(offset or 0)
        lim = int(limit)
        sql += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([off, lim])

    return db.query(sql, params)

def get_decor_by_id(decor_id: int) -> Optional[Dict[str, Any]]:
    """Lookup of a single decor by ID."""
    sql = "SELECT * FROM dbo.DecorOption WHERE DecorId = ?;"
    rows = db.query(sql, (decor_id,))
    return rows[0] if rows else None

def get_service_by_id(service_id: int) -> Optional[Dict[str, Any]]:
    """Lookup of a single service by ID."""
    sql = "SELECT * FROM dbo.ServiceOption WHERE ServiceId = ?;"
    rows = db.query(sql, (service_id,))
    return rows[0] if rows else None

def get_hall_by_id(hall_id: int) -> Optional[Dict[str, Any]]:
    """Lookup of a single hall by ID."""
    sql = "SELECT * FROM dbo.Hall WHERE HallId = ?;"
    rows = db.query(sql, (hall_id,))
    return rows[0] if rows else None

def get_decor_used_by_user(user_id: int) -> List[Dict[str, Any]]:
    """ Get decors used by a single user"""
    sql = """
    SELECT d.DecorId AS id,
           d.DecorName AS title,
           CONCAT(d.Category, COALESCE(' · ' + d.Theme, '')) AS subtitle,
           d.Region AS region,
           d.PhotoUrl AS photo
    FROM dbo.UserDecor ud
    INNER JOIN dbo.DecorOption d ON d.DecorId = ud.DecorId
    WHERE ud.UserId = ? AND ud.RelationType = 'USER'
    ORDER BY d.DecorName;
    """
    return db.query(sql, (user_id,))

def get_services_used_by_user(user_id: int) -> List[Dict[str, Any]]:
    """ Get services used by a single user"""
    sql = """
    SELECT s.ServiceId AS id,
           s.ServiceName AS title,
           COALESCE(s.ShortDescription, s.Subcategory) AS subtitle,
           s.Region AS region,
           s.PhotoUrl AS photo
    FROM dbo.UserServiceLink us
    INNER JOIN dbo.ServiceOption s ON s.ServiceId = us.ServiceId
    WHERE us.UserId = ? AND us.RelationType = 'USER'
    ORDER BY s.ServiceName;
    """
    return db.query(sql, (user_id,))

def get_halls_used_by_user(user_id: int) -> List[Dict[str, Any]]:
    """ Get halls used by a single user"""
    sql = """
    SELECT h.HallId AS id,
           h.HallName AS title,
           h.HallType AS subtitle,
           h.Region AS region,
           h.PhotoUrl AS photo
    FROM dbo.UserHall uh
    INNER JOIN dbo.Hall h ON h.HallId = uh.HallId
    WHERE uh.UserId = ? AND uh.RelationType = 'USER'
    ORDER BY h.HallName;
    """
    return db.query(sql, (user_id,))

def get_owned_items_by_user(user_id: int) -> List[Dict[str, Any]]:
    """ Get all items owned by a single user"""
    sql = """
    SELECT s.ServiceId AS id,
           s.ServiceName AS title,
           COALESCE(s.ShortDescription, s.Subcategory) AS subtitle,
           s.Region AS region,
           s.PhotoUrl AS photo,
           'Service' AS pill
    FROM dbo.UserServiceLink us
    INNER JOIN dbo.ServiceOption s ON s.ServiceId = us.ServiceId
    WHERE us.UserId = ? AND us.RelationType IN ('OWNER','OWNED','OWNER_OF')

    UNION ALL

    SELECT h.HallId AS id,
           h.HallName AS title,
           h.HallType AS subtitle,
           h.Region AS region,
           h.PhotoUrl AS photo,
           'Hall' AS pill
    FROM dbo.UserHall uh
    INNER JOIN dbo.Hall h ON h.HallId = uh.HallId
    WHERE uh.UserId = ? AND uh.RelationType IN ('OWNER','OWNED','OWNER_OF')

    UNION ALL

    SELECT d.DecorId AS id,
           d.DecorName AS title,
           CONCAT(d.Category, COALESCE(' · ' + d.Theme, '')) AS subtitle,
           d.Region AS region,
           d.PhotoUrl AS photo,
           'Decor' AS pill
    FROM dbo.UserDecor ud
    INNER JOIN dbo.DecorOption d ON d.DecorId = ud.DecorId
    WHERE ud.UserId = ? AND ud.RelationType IN ('OWNER','OWNED','OWNER_OF')

    ORDER BY title;
    """
    return db.query(sql, (user_id, user_id, user_id))

def get_decor_prices(
        search: Optional[str] = None,
        category: Optional[str] = None,
        available: Optional[bool] = None,
        region: Optional[str] = None,
        order_by: str = "MidPrice",   # MidPrice | DecorName | Region | Category
        ascending: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Return decor items with S/M/L prices and a computed MidPrice
    (medium if present, else avg of small/large, else whichever exists).

    Supports filters (category, region, available, search),
    sorting (DecorName, Region, Category, MidPrice),
    and optional paging (limit/offset).
    """
    order_map = {
        "DecorName": "d.DecorName",
        "Region":    "d.Region",
        "Category":  "d.Category",
        "MidPrice":  "mp.MidPrice",
    }
    order_col = order_map.get(order_by, "mp.MidPrice")
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
        d.PriceSmall,
        d.PriceMedium,
        d.PriceLarge,

        COALESCE(
            d.PriceMedium,
            CASE
              WHEN d.PriceSmall IS NOT NULL AND d.PriceLarge IS NOT NULL
                   THEN (d.PriceSmall + d.PriceLarge) / 2
              ELSE COALESCE(d.PriceSmall, d.PriceLarge)
            END
        ) AS MidPrice
    FROM dbo.DecorOption AS d
    OUTER APPLY (
        SELECT COALESCE(
            d.PriceMedium,
            CASE
              WHEN d.PriceSmall IS NOT NULL AND d.PriceLarge IS NOT NULL
                   THEN (d.PriceSmall + d.PriceLarge) / 2
              ELSE COALESCE(d.PriceSmall, d.PriceLarge)
            END
        ) AS MidPrice
    ) AS mp
    WHERE 1=1
    """
    params: List[Any] = []

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

    sql += f" ORDER BY {order_col} {order_dir}"

    if limit is not None:
        off = int(offset or 0)
        lim = int(limit)
        sql += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([off, lim])

    return db.query(sql, params)

def get_tables_name():
    """ Return tables names """
    sql = "SELECT name FROM sys.tables"
    return db.query(sql)

if __name__ == "__main__":
    # Demo printing of queries
    print("decorators:"); print_table(get_decorators())
    print("services:"); print_table(get_services())
    print("\nHalls:"); print_table(get_halls())
    print(get_decor_cards())
    print(get_user_by_user_name("Noa Hadad"))
    print("Users:"); print_table(get_users())
    print("\nTables:"); print_table(get_tables_name())