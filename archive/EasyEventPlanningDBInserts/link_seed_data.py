"""
link_seed_data_fixed.py
מכניס קשרים מפורשים לטבלאות הקישור החדשות, בלי להשתמש ב-scalar/query_one.
- Noa Hadad: 2 שירותים (USER), אולם (USER), קישוט בבעלות (OWNER).
- אידמפוטנטי (IF NOT EXISTS בכל INSERT).
"""

from server.gateway.DBgateway import DbGateway

# ===== עזרונים =====

def table_exists(db: DbGateway, table_name: str) -> bool:
    rows = db.query(
        "SELECT 1 FROM sys.tables WHERE name = ? AND schema_id = SCHEMA_ID('dbo');",
        (table_name,)
    )
    return bool(rows)

def fetch_id_by_name(db: DbGateway, table: str, id_col: str, name_col: str, name_val: str):
    rows = db.query(
        f"SELECT TOP 1 {id_col} AS Id FROM dbo.{table} WHERE {name_col} = ?;",
        (name_val,)
    )
    return rows[0]["Id"] if rows else None

def upsert_user_service(db: DbGateway, user_id: int, service_id: int, relation: str = "USER"):
    db.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM dbo.UserServiceLink
            WHERE UserId = ? AND ServiceId = ? AND RelationType = ?
        )
        INSERT INTO dbo.UserServiceLink(UserId, ServiceId, RelationType)
        VALUES (?, ?, ?);
        """,
        (user_id, service_id, relation, user_id, service_id, relation)
    )

def upsert_user_hall(db: DbGateway, user_id: int, hall_id: int, relation: str = "USER"):
    db.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM dbo.UserHall
            WHERE UserId = ? AND HallId = ? AND RelationType = ?
        )
        INSERT INTO dbo.UserHall(UserId, HallId, RelationType)
        VALUES (?, ?, ?);
        """,
        (user_id, hall_id, relation, user_id, hall_id, relation)
    )

def upsert_user_decor(db: DbGateway, user_id: int, decor_id: int, relation: str = "USER"):
    db.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM dbo.UserDecor
            WHERE UserId = ? AND DecorId = ? AND RelationType = ?
        )
        INSERT INTO dbo.UserDecor(UserId, DecorId, RelationType)
        VALUES (?, ?, ?);
        """,
        (user_id, decor_id, relation, user_id, decor_id, relation)
    )


# ===== main =====

def main():
    db = DbGateway()  # כמו בכל הסקריפטים שלך משתמשים ב-db.query / db.execute :contentReference[oaicite:6]{index=6}

    # בדיקת קיום טבלאות הקישור (בלי scalar/query_one)
    for t in ("UserDecor", "UserHall", "UserServiceLink"):
        if not table_exists(db, t):
            raise RuntimeError(f"Missing table dbo.{t}. Run the schema migration that adds it.")

    # IDs לפי שמות קיימים בנתונים שזרעת:
    # Users: Username
    noa_id = fetch_id_by_name(db, "Users", "UserId", "Username", "Noa Hadad")

    if noa_id:
        # Services: ServiceOption.ServiceName
        svc_quiz_id = fetch_id_by_name(db, "ServiceOption", "ServiceId", "ServiceName", "Interactive Quiz Show")  # Center :contentReference[oaicite:7]{index=7}
        svc_bubble_id = fetch_id_by_name(db, "ServiceOption", "ServiceId", "ServiceName", "Bubble Art Show")       # Center :contentReference[oaicite:8]{index=8}

        # Hall: Hall.HallName
        hall_id = fetch_id_by_name(db, "Hall", "HallId", "HallName", "Herzliya Banquet Center")  # Center :contentReference[oaicite:9]{index=9}
        if hall_id is None:
            hall_id = fetch_id_by_name(db, "Hall", "HallId", "HallName", "Tel Aviv Loft 22")      # Center (fallback) :contentReference[oaicite:10]{index=10}

        # Decor: DecorOption.DecorName
        decor_owner_id = fetch_id_by_name(
            db, "DecorOption", "DecorId", "DecorName", "Floral Centerpieces – Roses & Eucalyptus"
        )  # Center :contentReference[oaicite:11]{index=11}

        # === Inserts (idempotent) ===
        if svc_quiz_id:
            upsert_user_service(db, noa_id, svc_quiz_id, relation="USER")
        if svc_bubble_id:
            upsert_user_service(db, noa_id, svc_bubble_id, relation="USER")
        if hall_id:
            upsert_user_hall(db, noa_id, hall_id, relation="USER")
        if decor_owner_id:
            upsert_user_decor(db, noa_id, decor_owner_id, relation="OWNER")

        print("Linked Noa Hadad -> services(2 USER), hall(1 USER), decor(1 OWNER).")
    else:
        print("User 'Noa Hadad' not found. Skipping her links.")

    print("Done.")

if __name__ == "__main__":
    main()
