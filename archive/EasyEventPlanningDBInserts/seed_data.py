from datetime import date, time
from server.gateway.DBgateway import *


def seed() -> None:
    """Insert a rich set of demo data across all tables."""
    db = DbGateway()

    # Demo reset
    for t in ("EventServices", "UserServices", "Events", "Services", "Users"):
        db.execute(f"IF OBJECT_ID('dbo.{t}') IS NOT NULL DELETE FROM dbo.{t};")

    # Users
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

    # Services
    services = [
        ("DJ",           "Professional DJ with sound system", "Center",    12, None, 1500.00),
        ("Photography",  "Event photo & video",               "North",      0, None, 2200.00),
        ("Magician",     "Kids magic show",                   "Center",     5,  12,   900.00),
        ("Catering",     "Kosher buffet catering",            "Jerusalem",  0, None,  120.00),
        ("FacePainting", "Face painting for kids",            "Center",     3,  12,   500.00),
    ]
    db.execute_many(
        "INSERT INTO dbo.Services (ServiceType, ServiceDescription, Region, MinAge, MaxAge, Price) VALUES (?, ?, ?, ?, ?, ?);",
        services
    )

    # Map usernames/services to IDs
    user_id = {row["Username"]: row["UserId"] for row in db.query("SELECT UserId, Username FROM dbo.Users;")}
    service_id = {row["ServiceType"]: row["ServiceId"] for row in db.query("SELECT ServiceId, ServiceType FROM dbo.Services;")}

    # UserServices
    user_services = [
        (user_id["Noa Hadad"],        service_id["Photography"]),
        (user_id["Dan Keminzky"],    service_id["DJ"]),
        (user_id["Maya Merkovich"],  service_id["FacePainting"]),
        (user_id["Amir Sharabi"],    service_id["Catering"]),
        (user_id["Lior Levy"],       service_id["Magician"]),
        (user_id["Noa Hadad"],        service_id["Catering"]),
    ]
    db.execute_many("INSERT INTO dbo.UserServices (UserId, ServiceId) VALUES (?, ?);", user_services)

    # Events
    events = [
        (date(2025, 9, 1),  time(18, 0), "Birthday",    user_id["Maya Merkovich"]),
        (date(2025, 9, 5),  time(20, 0), "Wedding",     user_id["Dan Keminzky"]),
        (date(2025, 10, 3), time(11, 0), "Bar Mitzvah", user_id["Lior Levy"]),
        (date(2025, 10, 8), time(16, 0), "Happy hour",  user_id["Noa Hadad"]),
    ]
    db.execute_many(
        "INSERT INTO dbo.Events (EventDate, EventTime, EventType, ManagerUserId) VALUES (?, ?, ?, ?);",
        events
    )

    # EventServices
    event_key = {(str(row["EventDate"]), row["EventType"]): row["EventId"]
                 for row in db.query("SELECT EventId, EventDate, EventType FROM dbo.Events;")}
    event_services = [
        (event_key[(str(date(2025, 9, 1)),  "Birthday")],   service_id["FacePainting"]),
        (event_key[(str(date(2025, 9, 1)),  "Birthday")],   service_id["Magician"]),
        (event_key[(str(date(2025, 9, 5)),  "Wedding")],    service_id["DJ"]),
        (event_key[(str(date(2025, 9, 5)),  "Wedding")],    service_id["Photography"]),
        (event_key[(str(date(2025, 9, 5)),  "Wedding")],    service_id["Catering"]),
        (event_key[(str(date(2025, 10, 3)), "Bar Mitzvah")], service_id["Photography"]),
        (event_key[(str(date(2025, 10, 3)), "Bar Mitzvah")], service_id["Catering"]),
        (event_key[(str(date(2025, 10, 8)), "Happy hour")], service_id["DJ"]),
        (event_key[(str(date(2025, 10, 8)), "Happy hour")], service_id["Catering"]),
        (event_key[(str(date(2025, 10, 8)), "Happy hour")], service_id["Photography"]),
    ]
    db.execute_many("INSERT INTO dbo.EventServices (EventId, ServiceId) VALUES (?, ?);", event_services)

    print("Bulk data seeding completed successfully.")


if __name__ == "__main__":
    seed()
