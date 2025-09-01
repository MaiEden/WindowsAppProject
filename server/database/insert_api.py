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
