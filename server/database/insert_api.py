import pyodbc
from typing import List, Dict, Any, Optional, Sequence
from decimal import Decimal
from server.gateway.DBgateway import DbGateway

db = DbGateway()
def add_user(
    phone: str,
    username: str,
    password_hash: str,
    region: str
) -> int:
    """Add a user to the database."""
    sql = "INSERT INTO dbo.Users (Phone, Username, PasswordHash, Region) VALUES (?, ?, ?, ?);"
    params = (phone, username, password_hash, region)
    return db.execute(sql, params)

def add_decor_option(d: Dict[str, Any]) -> int:
    cols = [
        "DecorName","Category","Theme","Description",
        "Indoor","RequiresElectricity",
        "PriceSmall","PriceMedium","PriceLarge","DeliveryFee",
        "Region","VendorName","ContactPhone","ContactEmail",
        "PhotoUrl","LeadTimeDays","CancellationPolicy","Available"
    ]
    placeholders = ",".join("?" for _ in cols)

    sql = f"""
        INSERT INTO dbo.DecorOption ({",".join(cols)})
        OUTPUT INSERTED.DecorId
        VALUES ({placeholders});
    """
    params = tuple(d.get(c) for c in cols)

    rows = db.query(sql, params)               # returns list[dict]
    if not rows or "DecorId" not in rows[0]:
        raise Exception("Insert DecorOption failed: no id returned")
    return int(rows[0]["DecorId"])

def link_user_decor(user_id: int, decor_id: int, relation: str = "OWNER") -> int:
    sql = "INSERT INTO dbo.UserDecor (UserId, DecorId, RelationType) VALUES (?, ?, ?);"
    return db.execute(sql, (user_id, decor_id, relation))