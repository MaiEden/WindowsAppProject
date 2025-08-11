"""
seed_data.py
Bulk insert demo data for the Events app.
"""
from datetime import date, time
from server.database.db_config import get_connection  # noqa: E402


def seed() -> None:
    """Insert a rich set of demo data across all tables."""
    with get_connection() as conn:
        cur = conn.cursor()

        # Demo reset (safe to comment out in production)
        for t in ("EventServices", "UserServices", "Events", "Services", "Users"):
            cur.execute(f"IF OBJECT_ID('dbo.{t}') IS NOT NULL DELETE FROM dbo.{t};")
        conn.commit()

        # Users
        users = [
            ("050-1111111", "Noa Hadad",       "hash:noa",  "Rehovot"),
            ("050-2222222", "Dan Keminzky",    "hash:dan",  "Rishon Lezion"),
            ("050-3333333", "Maya Merkovich",  "hash:maya", "Nes Ziona"),
            ("050-4444444", "Amir Sharabi",    "hash:amir", "Gedera"),
            ("050-5555555", "Lior Levy",       "hash:lior", "Jerusalem"),
        ]
        cur.fast_executemany = True
        cur.executemany(
            "INSERT INTO dbo.Users (Phone, Username, PasswordHash, Region) VALUES (?, ?, ?, ?);",
            users
        )
        conn.commit()

        # Services
        services = [
            ("DJ",           "Professional DJ with sound system", "Center",    12, None, 1500.00),
            ("Photography",  "Event photo & video",               "North",      0, None, 2200.00),
            ("Magician",     "Kids magic show",                   "Center",     5,  12,   900.00),
            ("Catering",     "Kosher buffet catering",            "Jerusalem",  0, None,  120.00),
            ("FacePainting", "Face painting for kids",            "Center",     3,  12,   500.00),
        ]
        cur.executemany(
            "INSERT INTO dbo.Services (ServiceType, ServiceDescription, Region, MinAge, MaxAge, Price) "
            "VALUES (?, ?, ?, ?, ?, ?);",
            services
        )
        conn.commit()

        # Map users/services to ids
        cur.execute("SELECT UserId, Username FROM dbo.Users;")
        user_id = {u: i for i, u in cur.fetchall()}

        cur.execute("SELECT ServiceId, ServiceType FROM dbo.Services;")
        service_id = {t: i for i, t in cur.fetchall()}

        # UserServices (unchanged, uses the keys as you wrote them)
        user_services = [
            (user_id["Noa Hadad"],        service_id["Photography"]),
            (user_id["Dan Keminzky"],    service_id["DJ"]),
            (user_id["Maya Merkovich"],  service_id["FacePainting"]),
            (user_id["Amir Sharabi"],    service_id["Catering"]),
            (user_id["Lior Levy"],       service_id["Magician"]),
            (user_id["Noa Hadad"],        service_id["Catering"]),
        ]
        cur.executemany("INSERT INTO dbo.UserServices (UserId, ServiceId) VALUES (?, ?);", user_services)
        conn.commit()

        # Events
        events = [
            (date(2025, 9, 1),  time(18, 0), "Birthday",    user_id["Maya Merkovich"]),
            (date(2025, 9, 5),  time(20, 0), "Wedding",     user_id["Dan Keminzky"]),
            (date(2025, 10, 3), time(11, 0), "Bar Mitzvah", user_id["Lior Levy"]),
            (date(2025, 10, 8), time(16, 0), "Happy hour",  user_id["Noa Hadad"]),
        ]
        cur.executemany(
            "INSERT INTO dbo.Events (EventDate, EventTime, EventType, ManagerUserId) VALUES (?, ?, ?, ?);",
            events
        )
        conn.commit()

        # Link Events <-> Services (replaces the old Attractions/EventAttractions sections)
        # Build a key to find event IDs by (date, type)
        cur.execute("SELECT EventId, EventDate, EventType FROM dbo.Events;")
        event_key = {(str(d), t): i for i, d, t in cur.fetchall()}

        event_services = [
            # Birthday -> FacePainting + Magician
            (event_key[(str(date(2025, 9, 1)),  "Birthday")],   service_id["FacePainting"]),
            (event_key[(str(date(2025, 9, 1)),  "Birthday")],   service_id["Magician"]),

            # Wedding -> DJ + Photography + Catering
            (event_key[(str(date(2025, 9, 5)),  "Wedding")],    service_id["DJ"]),
            (event_key[(str(date(2025, 9, 5)),  "Wedding")],    service_id["Photography"]),
            (event_key[(str(date(2025, 9, 5)),  "Wedding")],    service_id["Catering"]),

            # Bar Mitzvah -> Photography + Catering
            (event_key[(str(date(2025, 10, 3)), "Bar Mitzvah")], service_id["Photography"]),
            (event_key[(str(date(2025, 10, 3)), "Bar Mitzvah")], service_id["Catering"]),

            # Happy hour -> DJ + Catering + Photography
            (event_key[(str(date(2025, 10, 8)), "Happy hour")], service_id["DJ"]),
            (event_key[(str(date(2025, 10, 8)), "Happy hour")], service_id["Catering"]),
            (event_key[(str(date(2025, 10, 8)), "Happy hour")], service_id["Photography"]),
        ]
        cur.executemany("INSERT INTO dbo.EventServices (EventId, ServiceId) VALUES (?, ?);", event_services)
        conn.commit()

        print("Bulk data seeding completed successfully.")

if __name__ == "__main__":
    seed()
