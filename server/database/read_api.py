"""
read_api.py
Read-only API to fetch data and aggregated reports from the Events app schema

This module provides:
-------------------------
- get_users():            Basic list of users.
- get_services():         Services catalog (with price/age range/region).
- get_events():           Events with the manager (user) name.
- get_user_services():    Flat mapping of which external_services each user offers.
- report_users_with_services_and_events():
                         Per-user aggregation: offered external_services + events managed.
- report_events_with_services_and_manager():
                         Per-event aggregation: manager + external_services planned.
"""

import pyodbc
from typing import List, Dict, Any, Optional, Sequence
from db_config import get_connection
from decimal import Decimal


def _fetchall_dicts(cur: pyodbc.Cursor) -> List[Dict[str, Any]]:
    """
    Convert the current cursor resultset into a list of dictionaries.

    Args:
        cur: An active pyodbc cursor positioned after `execute()`.

    Returns:
        A list of dictionaries where keys are column names and values are row values.
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

    # Infer columns if not provided; preserve a stable order
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

    # Compute widths per column
    widths = []
    for col in columns:
        col_width = len(str(col))
        for r in rows:
            col_width = max(col_width, len(fmt(r.get(col))))
        widths.append(col_width)

    # Helpers to align cells
    def is_number(v: Any) -> bool:
        return isinstance(v, (int, float, Decimal))

    def cell(val: Any, w: int) -> str:
        text = fmt(val)
        return text.rjust(w) if is_number(val) else text.ljust(w)

    # Print header
    header = " | ".join(str(col).ljust(w) for col, w in zip(columns, widths))
    sep = "-+-".join("-" * w for w in widths)
    print(header)
    print(sep)

    # Print rows
    for r in rows:
        line = " | ".join(cell(r.get(col), w) for col, w in zip(columns, widths))
        print(line)


def get_users() -> List[Dict[str, Any]]:
    """
    Fetch all users with basic fields.

    Returns List of dicts: [{UserId, Phone, Username, Region}, ...], ordered by Username.
    """
    sql = "SELECT UserId, Phone, Username, Region FROM dbo.Users ORDER BY Username;"
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return _fetchall_dicts(cur)


def get_services() -> List[Dict[str, Any]]:
    """
    Fetch the external_services catalog.

    Returns list of dicts: [{ServiceId, ServiceType, ServiceDescription, Region, MinAge, MaxAge, Price}, ...]
        ordered by ServiceType.
    """
    sql = """
    SELECT ServiceId,
           ServiceType,
           ISNULL(ServiceDescription,'') AS ServiceDescription,
           Region,
           MinAge,
           MaxAge,
           Price
    FROM dbo.Services
    ORDER BY ServiceType;
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return _fetchall_dicts(cur)


def get_events() -> List[Dict[str, Any]]:
    """
    Fetch all events including the manager's username.

    Returns list of dicts: [{EventId, EventDate, EventTime, EventType, Manager}, ...]
        ordered by date and time.
    """
    sql = """
    SELECT e.EventId,
           e.EventDate,
           CONVERT(NVARCHAR(8), e.EventTime, 108) AS EventTime,
           e.EventType,
           u.Username AS Manager
    FROM dbo.Events e
    INNER JOIN dbo.Users u ON u.UserId = e.ManagerUserId
    ORDER BY e.EventDate, e.EventTime;
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return _fetchall_dicts(cur)


def get_user_services() -> List[Dict[str, Any]]:
    """
    Fetch a flattened map of which external_services each user offers.

    Returns list of dicts: [{Username, ServiceType}, ...], ordered by Username then ServiceType.
    """
    sql = """
    SELECT u.Username, s.ServiceType
    FROM dbo.UserServices us
    INNER JOIN dbo.Users u ON u.UserId = us.UserId
    INNER JOIN dbo.Services s ON s.ServiceId = us.ServiceId
    ORDER BY u.Username, s.ServiceType;
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return _fetchall_dicts(cur)


def report_users_with_services_and_events() -> List[Dict[str, Any]]:
    """
    Per-user aggregation:
      - ServicesOffered: CSV of distinct service types the user offers.
      - EventsManaged:   CSV of distinct "EventDate EventType" labels the user manages.

    Returns:
        List of dicts: [{UserId, Username, Phone, Region, ServicesOffered, EventsManaged}, ...]
        ordered by Username.
    """
    sql = """
    SELECT
        u.UserId,
        u.Username,
        u.Phone,
        u.Region,

        ISNULL((
            SELECT STRING_AGG(d.ServiceType, ', ')
            FROM (
                SELECT DISTINCT s.ServiceType
                FROM dbo.UserServices us2
                INNER JOIN dbo.Services s ON s.ServiceId = us2.ServiceId
                WHERE us2.UserId = u.UserId
            ) AS d
        ), 'None') AS ServicesOffered,

        ISNULL((
            SELECT STRING_AGG(d.EventLabel, ' | ')
            FROM (
                SELECT DISTINCT CONVERT(NVARCHAR(30), e.EventDate) + ' ' + e.EventType AS EventLabel
                FROM dbo.Events e
                WHERE e.ManagerUserId = u.UserId
            ) AS d
        ), 'None') AS EventsManaged

    FROM dbo.Users u
    ORDER BY u.Username;
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return _fetchall_dicts(cur)


def report_events_with_services_and_manager() -> List[Dict[str, Any]]:
    """
    Per-event aggregation:
      - Manager:  the username of the event manager.
      - Services: CSV of distinct service types planned for the event.

    Returns:
        List of dicts: [{EventId, EventDate, EventTime, EventType, Manager, Services}, ...]
        ordered by date and time.
    """
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
                SELECT DISTINCT s.ServiceType
                FROM dbo.EventServices es
                INNER JOIN dbo.Services s ON s.ServiceId = es.ServiceId
                WHERE es.EventId = e.EventId
            ) AS d
        ), 'None') AS Services
    FROM dbo.Events e
    INNER JOIN dbo.Users u ON u.UserId = e.ManagerUserId
    ORDER BY e.EventDate, e.EventTime;
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return _fetchall_dicts(cur)


if __name__ == "__main__":
    # Smoke tests: print a sample of each endpoint so you can see the shape quickly.
    from pprint import pprint
    print("Users:"); print_table(get_users())
    print("\nServices:"); print_table(get_services())
    print("\nEvents:"); print_table(get_events())
    print("\nUserServices:"); print_table(get_user_services())
    print("\nReport: Users with external_services & events"); print_table(report_users_with_services_and_events())
    print("\nReport: Events with external_services & manager"); print_table(report_events_with_services_and_manager())
