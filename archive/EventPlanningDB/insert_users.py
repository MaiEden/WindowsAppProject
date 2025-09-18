"""
insert_users.py
insert users demo data into the Events app database.

What this script does:
- Clears existing rows from users table.
- Inserts a small set of demo users.
"""
from server.gateway.DBgateway import DbGateway

def insert_users() -> None:
    """
    Populate the database with deterministic demo data.

    Steps:
      1) Wipe existing data from users table.
      2) Insert demo users.
      3) Read back user IDs and build a name->id map.
    """
    db = DbGateway()

    # 1) Reset existing data
    db.execute(f"IF OBJECT_ID('dbo.Users', 'U') IS NOT NULL DELETE FROM dbo.Users;")

    # 2) Users
    users = [
        ("050-1111111", "Noa Hadad",       "hash:noa",  "Rehovot"),
        ("050-2222222", "Dan Keminzky",    "hash:dan",  "Rishon Lezion"),
        ("050-3333333", "Maya Merkovich",  "hash:maya", "Nes Ziona"),
        ("050-4444444", "Amir Sharabi",    "hash:amir", "Gedera"),
        ("050-5555555", "Lior Levy",       "hash:lior", "Jerusalem"),
    ]
    db.execute_many(
        "INSERT INTO dbo.Users (Phone, Username, PasswordHash, Region) VALUES (?, ?, ?, ?);",
        users
    )

    print(f"insert users completed successfully with {len(users)} users.")

if __name__ == "__main__":
    insert_users()