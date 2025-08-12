"""
db_config.py
Centralized configuration and connection helpers for SQL Server (somee.com).

How to use:
    from db_config import get_connection
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        print(cur.fetchone())
"""

import os
import pyodbc


# --- Connection parameters ---
SERVER = os.getenv("DB_SERVER", "EasyEventPlanningDB.mssql.somee.com")
DATABASE = os.getenv("DB_DATABASE", "EasyEventPlanningDB")
USERNAME = os.getenv("DB_USERNAME", "MaiEden_SQLLogin_1")
PASSWORD = os.getenv("DB_PASSWORD", "1ujq66i81r")
DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

def build_connection_string() -> str:
    """
    Build a secure connection string for somee.com SQL Server.

    Returns:
        str: A full ODBC connection string.
    """
    return (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER},1433;"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )


def get_connection(autocommit: bool = False) -> pyodbc.Connection:
    """
    Create and return a pyodbc connection.

    Args:
        autocommit: If True, autocommit is enabled on the connection.

    Returns:
        pyodbc.Connection: An open connection to the database.
    """
    return pyodbc.connect(build_connection_string(), autocommit=autocommit)


if __name__ == "__main__":
    # Quick sanity check you can run manually.
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT @@VERSION;")
        print(cur.fetchone()[0])