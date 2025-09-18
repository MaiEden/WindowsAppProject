"""
link_seed_data.py
Reset and insert demo relationships for user "Noa Hadad" into link tables.

Behavior:
-1 DELETE all existing links for Noa.
- Then re-insert desired links:
  - Services (USER): 3
  - Halls    (USER): 3
  - Decor    (USER): 3
  - Decor    (OWNER): 2

Notes:
- Skip-missing policy: if a referenced name is not found, we skip it and continue.
"""

from typing import List, Tuple, Optional
from server.gateway.DBgateway import DbGateway

# ===================== Helpers =====================

def table_exists(db: DbGateway, table_name: str) -> bool:
    """Return True if dbo.<table_name> exists."""
    rows = db.query(
        "SELECT 1 FROM sys.tables WHERE name = ? AND schema_id = SCHEMA_ID('dbo');",
        (table_name,)
    )
    return bool(rows)

def fetch_id_by_name(
    db: DbGateway,
    table: str,
    id_col: str,
    name_col: str,
    name_val: str
) -> Optional[int]:
    """Fetch a single Id by exact name (TOP 1). Return None if not found."""
    rows = db.query(
        f"SELECT TOP 1 {id_col} AS Id FROM dbo.{table} WHERE {name_col} = ?;",
        (name_val,)
    )
    return rows[0]["Id"] if rows else None

def fetch_ids_by_names(
    db: DbGateway,
    table: str,
    id_col: str,
    name_col: str,
    names: List[str]
) -> List[Tuple[str, int]]:
    """
    Fetch IDs for a list of names. Returns a list of (name, id) pairs
    only for names that exist. Missing names are silently skipped.
    """
    results: List[Tuple[str, int]] = []
    for n in names:
        _id = fetch_id_by_name(db, table, id_col, name_col, n)
        if _id is not None:
            results.append((n, _id))
    return results

def upsert_user_service(db: DbGateway, user_id: int, service_id: int, relation: str = "USER") -> None:
    """Insert into dbo.UserServiceLink if not already present for (UserId, ServiceId, RelationType)."""
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

def upsert_user_hall(db: DbGateway, user_id: int, hall_id: int, relation: str = "USER") -> None:
    """Insert into dbo.UserHall if not already present for (UserId, HallId, RelationType)."""
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

def upsert_user_decor(db: DbGateway, user_id: int, decor_id: int, relation: str) -> None:
    """Insert into dbo.UserDecor if not already present for (UserId, DecorId, RelationType)."""
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

def clear_all_links_for_user(db: DbGateway, user_id: int) -> None:
    """
    Remove ALL existing links for the given user from the three link tables.
    This gives a clean slate before we re-seed desired connections.
    """
    db.execute("DELETE FROM dbo.UserServiceLink WHERE UserId = ?;", (user_id,))
    db.execute("DELETE FROM dbo.UserHall        WHERE UserId = ?;", (user_id,))
    db.execute("DELETE FROM dbo.UserDecor       WHERE UserId = ?;", (user_id,))

# ===================== Main =====================

def main() -> None:
    db = DbGateway()

    # Ensure link tables exist (fail fast with a clear message)
    for t in ("UserDecor", "UserHall", "UserServiceLink"):
        if not table_exists(db, t):
            raise RuntimeError(f"Missing table dbo.{t}. Run the schema migration that adds it.")

    # -------- Source names --------
    target_username = "Noa Hadad"

    service_names_user = [
        "Stand-up Comedy Night",
        "Live Caricature Station",
        "Interactive Quiz Show",
    ]

    hall_names_user = [
        "Ashdod Event Hall",
        "Ashkelon Coastal Venue",
        "Bat Yam Event Loft",
    ]

    decor_names_user = [
        "Balloons – Classic Arch",
        "Floral Centerpieces – Roses & Eucalyptus",
        "Decorative Tableware – Gold Rim Set",
    ]

    # OWNER applies to Decor
    decor_names_owner = [
        "Linens – Pastel Mix",
        "Backdrop – Velvet Curtain Wall",
    ]

    # -------- Look up Noa's UserId --------
    noa_id = fetch_id_by_name(db, "Users", "UserId", "Username", target_username)
    if not noa_id:
        print("User 'Noa Hadad' not found. Skipping all links.")
        print("Done.")
        return

    # -------- Clean slate: delete existing user links --------
    clear_all_links_for_user(db, noa_id)

    # -------- Resolve IDs from names --------
    svc_pairs_user    = fetch_ids_by_names(db, "ServiceOption", "ServiceId", "ServiceName", service_names_user)
    hall_pairs_user   = fetch_ids_by_names(db, "Hall",          "HallId",    "HallName",   hall_names_user)
    decor_pairs_user  = fetch_ids_by_names(db, "DecorOption",   "DecorId",   "DecorName",  decor_names_user)
    decor_pairs_owner = fetch_ids_by_names(db, "DecorOption",   "DecorId",   "DecorName",  decor_names_owner)

    # -------- Insert desired links --------
    for _, sid in svc_pairs_user:
        upsert_user_service(db, noa_id, sid, relation="USER")

    for _, hid in hall_pairs_user:
        upsert_user_hall(db, noa_id, hid, relation="USER")

    for _, did in decor_pairs_user:
        upsert_user_decor(db, noa_id, did, relation="USER")

    for _, did in decor_pairs_owner:
        upsert_user_decor(db, noa_id, did, relation="OWNER")

    # -------- Compact summary --------
    print(
        f"Reset & linked Noa Hadad -> "
        f"services(USER:{len(svc_pairs_user)}), "
        f"halls(USER:{len(hall_pairs_user)}), "
        f"decor(USER:{len(decor_pairs_user)}, OWNER:{len(decor_pairs_owner)})."
    )
    print("Done.")

if __name__ == "__main__":
    main()