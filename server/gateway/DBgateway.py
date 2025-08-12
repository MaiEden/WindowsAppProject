import pyodbc
from .db_config import get_connection
from typing import List, Dict, Any

class DbGateway:
    """Gateway for SQL Server operations"""
    def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Run SELECT and return all rows as list of dicts {column: value}"""
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, params or ())

                # Extract column names from cursor.description
                columns = [desc[0] for desc in cur.description]

                # Convert each row (tuple) to dict
                rows = [dict(zip(columns, row)) for row in cur.fetchall()]
                return rows
        except pyodbc.Error as e:
            print(f"[DbGateway] Query error: {e}")
            return []

    def execute(self, sql: str, params: tuple = None, commit: bool = True) -> int:
        """Run INSERT/UPDATE/DELETE and return affected rows"""
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, params or ())
                if commit:
                    conn.commit()
                return cur.rowcount
        except pyodbc.Error as e:
            print(f"[DbGateway] Execute error: {e}")
            return 0

    def execute_many(self, sql: str, params_list: list, commit: bool = True) -> int:
        """Run executemany for bulk inserts/updates"""
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.fast_executemany = True
                cur.executemany(sql, params_list)
                if commit:
                    conn.commit()
                return cur.rowcount
        except pyodbc.Error as e:
            print(f"[DbGateway] ExecuteMany error: {e}")
            return 0
