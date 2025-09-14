"""
seed_data.py
Seeds demo data into the Events app database.

What this script does:
- Clears existing rows from the core tables (Users, Hall, Event, and the link tables).
- Inserts a small set of demo users.
- Inserts a few demo events referencing the inserted users.
- Inserts a larger demo catalog of halls with photos and descriptions.

Safety notes:
- This script deletes all data from tables: EventService, UserService, Event, Hall, Users.
  Make sure you are connected to the correct database before running.
- Designed for development and demos; do not run against production data.

Usage:
    python seed_data.py

Requirements:
    - server.gateway.DBgateway.DbGateway must point to the target DB.
"""

from datetime import date, time
from server.gateway.DBgateway import DbGateway


def seed() -> None:
    """
    Populate the database with deterministic demo data.

    Steps:
      1) Wipe existing data from dependent tables to avoid FK conflicts.
      2) Insert demo users.
      3) Read back user IDs and build a name->id map.
      4) Insert demo events referencing those user IDs.
      5) Insert a catalog of demo halls (name, type, region, pricing, photo, etc.).
    """
    db = DbGateway()

    # 1) Reset existing data (delete in FK-safe order)
    for t in ("EventService", "UserService", "Event", "Hall", "Users"):
        db.execute(f"IF OBJECT_ID('dbo.{t}', 'U') IS NOT NULL DELETE FROM dbo.{t};")

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

    # 3) Map IDs: read back inserted users and build a lookup for FK references
    user_rows = db.query("SELECT UserId, Username FROM dbo.Users;")
    user_id = {row["Username"]: row["UserId"] for row in user_rows}

    # 4) Events
    events = [
        (date(2025, 9, 1),  time(18, 0), "Birthday",    user_id["Maya Merkovich"]),
        (date(2025, 9, 5),  time(20, 0), "Wedding",     user_id["Dan Keminzky"]),
        (date(2025, 10, 3), time(11, 0), "Bar Mitzvah", user_id["Lior Levy"]),
        (date(2025, 10, 8), time(16, 0), "Happy hour",  user_id["Noa Hadad"]),
    ]
    db.execute_many(
        "INSERT INTO dbo.Event (EventDate, EventTime, EventType, ManagerUserId) VALUES (?, ?, ?, ?);",
        events
    )

    # 5) Halls (sample subset shown; extend as needed)
    # === Halls (start of 50) ===
    halls = [
        ("Tel Aviv Loft 22", "Loft", 120, "Center", 32.0853, 34.7818,
         "Industrial-chic loft with high ceilings, urban brick walls, and stylish lighting. Perfect for boutique weddings, private parties, and modern product launches.",
         500.00, None, 120.00, 1, 1,
         "050-1234567", "book@loft22.example", "https://loft22.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/TelAviLoft22.jpg"),

        ("Jerusalem Synagogue Hall", "Synagogue Hall", 200, "Jerusalem", 31.7683, 35.2137,
         "Traditional synagogue hall with wood design and warm lighting. Frequently used for weddings, Bar/Bat Mitzvahs, and community gatherings.",
         420.00, None, 110.00, 0, 1,
         "02-555-1111", "events@synagogue.example", "https://synagogue.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/JerusalemSynagoguHall.jpg"),

        ("Haifa Garden Venue", "Garden Venue", 350, "North", 32.7940, 34.9896,
         "Outdoor garden surrounded by waterfalls, green lawns, and romantic lighting. Ideal for large weddings, receptions, and concerts under the stars.",
         None, 10000.00, None, 1, 1,
         "04-9876543", "info@gardenvenue.example", "https://gardenvenue.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/HaifGardenVenue.jpg"),

        ("Herzliya Banquet Center", "Banquet Hall", 500, "Center", 32.1656, 34.8436,
         "Modern banquet hall with LED lighting, spacious stage, and central dance floor. Great for weddings, conferences, and formal galas.",
         1200.00, 15000.00, 150.00, 1, 1,
         "09-1234567", "sales@banquetcenter.example", "https://banquetcenter.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/HerzliyBanquetCenter.jpg"),

        ("Dead Sea Hotel Ballroom", "Hotel Ballroom", 400, "South", 31.5590, 35.4732,
         "Luxurious ballroom with chandeliers, sea views, and full catering. Popular for destination weddings, retreats, and elegant dinners.",
         2000.00, 20000.00, 180.00, 1, 1,
         "08-7654321", "events@hotelballroom.example", "https://hotelballroom.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/DeadSeaHotelBallroom.jpg"),

        ("Golan Heights Banquet Hall", "Banquet Hall", 280, "North", 32.9925, 35.6900,
         "Spacious banquet hall in the Golan, surrounded by scenic views. Designed for weddings, Bar/Bat Mitzvahs, and corporate events.",
         700.00, 8000.00, 140.00, 1, 0,
         "04-5551212", "events@golanbanquet.example", "https://golanbanquet.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/GolaHeightsBanquetHall.jpg"),

        ("Ashdod Event Hall", "Event Hall", 600, "South", 31.8014, 34.6435,
         "Modern event hall with industrial design and flexible seating arrangements. Popular for weddings, exhibitions, and concerts.",
         1000.00, 12000.00, 100.00, 1, 0,
         "08-9990000", "info@ashdodevent.example", "https://ashdodevent.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/AshdodEvenHall.jpg"),

        ("Caesarea Luxury Villa", "Villa", 100, "Center", 32.5000, 34.9000,
         "Exclusive villa with a pool, beachfront access, and elegant design. Ideal for boutique weddings and private retreats.",
         1500.00, 18000.00, 250.00, 1, 1,
         "054-1112233", "villa@luxury.example", "https://luxuryvilla.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/CaesareaLuxuryVill.jpg"),

        ("Herzliya Restaurant Venue", "Restaurant Venue", 200, "Center", 32.1656, 34.8436,
         "Fine-dining restaurant venue with private rooms and outdoor seating. Perfect for birthdays, anniversaries, and intimate weddings.",
         900.00, 10000.00, 140.00, 1, 1,
         "09-4445555", "dining@herzliya.example", "https://herzrestaurant.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/HerzliyaRestaurantVenue.jpg"),

        ("Zichron Banquet Hall", "Banquet Hall", 350, "North", 32.5667, 34.9500,
         "Banquet hall located in Zichron Yaakov, surrounded by greenery. Designed for weddings, large dinners, and family celebrations.",
         950.00, 11000.00, 150.00, 1, 1,
         "04-1239876", "zichron@banquethall.example", "https://zichronbanquet.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/ZichronBanqueHall.jpg"),

        ("Bat Yam Event Loft", "Loft", 90, "Center", 32.0230, 34.7519,
         "Modern loft with floor-to-ceiling windows and minimalist décor. Perfect for birthdays, cocktail events, and private parties.",
         400.00, 5000.00, 80.00, 0, 1,
         "03-1112222", "loft@batyamevents.example", "https://batyamevents.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/BatYamEventLoft.jpg"),

        ("Eilat Beach Club", "Beach Venue", 300, "South", 29.5577, 34.9519,
         "Vibrant beach venue with stage, cocktail bar, and direct sea access. Ideal for concerts, weddings, and summer celebrations.",
         600.00, 15000.00, None, 0, 0,
         "08-2224444", "info@beachclub.example", "https://beachclub.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/EilateachClub.jpg"),

        ("Petah Tikva Grand Banquet", "Banquet Hall", 480, "Center", 32.0918, 34.8850,
         "Large banquet hall with LED walls, premium sound, and spacious dance floor. Designed for weddings and galas.",
         1100.00, 14000.00, 140.00, 1, 1,
         "03-8889999", "grand@banquetptk.example", "https://banquetptk.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/PetahTikvaGrandBnquet.jpg"),

        ("Nazareth Olive Garden Venue", "Garden Venue", 220, "North", 32.6996, 35.3035,
         "Romantic olive garden with outdoor dining and string lighting. Popular for weddings, receptions, and private events.",
         None, 6000.00, 90.00, 1, 0,
         "04-7654321", "garden@nazareth.example", "https://nazarethgarden.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/photo-1470770841072-f978cf4d019e.jpg"),

        ("Beer Sheva Cultural Center", "Event Hall", 350, "South", 31.2520, 34.7915,
         "Spacious event hall with a stage and exhibition space. Frequently used for weddings, concerts, and community gatherings.",
         500.00, 7000.00, 120.00, 1, 1,
         "08-3334444", "culture@beersheva.example", "https://beershevacenter.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/BeerShevaCulturalCenter.jpg"),

        ("Holon Modern Loft", "Loft", 110, "Center", 32.0158, 34.7874,
         "Contemporary loft with exposed brick and open plan. Popular for private parties, launches, and creative events.",
         450.00, 5500.00, 85.00, 1, 1,
         "03-2223333", "holon@modernloft.example", "https://holonloft.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/HolnModernLoft.jpg"),

        ("Tiberias Lake Ballroom", "Hotel Ballroom", 270, "North", 32.7959, 35.5313,
         "Elegant ballroom with stunning views of the Sea of Galilee. A top choice for weddings and luxury celebrations.",
         900.00, 12000.00, 150.00, 1, 1,
         "04-1119999", "lake@tiberiasvenue.example", "https://tiberiasvenue.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/TiberiasLakeBallrom.jpg")
        ,
        ("Rosh Pina Garden Villa", "Villa", 90, "North", 32.9680, 35.5427,
         "Charming villa surrounded by greenery, featuring an intimate pool area and spacious garden. Great for boutique weddings and private celebrations.",
         850.00, 9500.00, 160.00, 1, 1,
         "04-1122334", "villa@roshpina.example", "https://roshpinavilla.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/RoshPinaGardenVilla.jpg"),

        ("Kiryat Gat Synagogue Hall", "Synagogue Hall", 180, "South", 31.6100, 34.7650,
         "Spacious synagogue hall designed for Bar Mitzvahs, weddings, and community events. Includes updated seating and stage.",
         300.00, 4000.00, 80.00, 0, 1,
         "08-5671234", "synagogue@kiryatgat.example", "https://kiryatgatshul.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/KiryatatSynagogueHall.jpg"),

        ("Modiin Event Center", "Banquet Hall", 420, "Center", 31.8928, 35.0119,
         "Modern banquet hall with customizable seating, advanced lighting, and professional catering services. Perfect for large weddings and galas.",
         1300.00, 16000.00, 145.00, 1, 1,
         "08-3216549", "modiin@eventcenter.example", "https://modiineventcenter.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/ModiiEventCenter.jpg"),

        ("Ashkelon Coastal Venue", "Garden Venue", 240, "South", 31.6688, 34.5715,
         "Coastal garden with cabanas, live music stage, and romantic lighting. Designed for weddings and seaside events.",
         650.00, 11000.00, None, 0, 0,
         "08-3219987", "coastal@ashkelon.example", "https://ashkelonvenue.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/AshkeloCoastalVenue.jpg"),

        ("Herzliya Marina Ballroom", "Hotel Ballroom", 220, "Center", 32.1656, 34.8436,
         "Elegant ballroom overlooking the marina, offering luxurious décor and catering. Suitable for weddings and formal dinners.",
         2000.00, 18000.00, 280.00, 1, 1,
         "09-9988776", "yacht@herzliya.example", "https://herzliyayacht.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/HerzliyaMarinBallroom.jpg"),

        ("Tel Aviv Seaside Ballroom", "Banquet Hall", 380, "Center", 32.0809, 34.7806,
         "High-end ballroom with sea view terraces, crystal chandeliers, and full-service catering. Ideal for luxury weddings.",
         1800.00, 19000.00, 220.00, 1, 1,
         "03-2225555", "seaside@ballroom.example", "https://seasideballroom.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/TelAvivSeasideallroom.jpg"),

        ("Dimona Celebration Hall", "Event Hall", 280, "South", 31.0700, 35.0300,
         "Modern celebration hall with large stage, professional lighting, and dance floor. Frequently used for weddings and corporate events.",
         400.00, 6000.00, 95.00, 1, 1,
         "08-6782345", "dimona@celebration.example", "https://dimonaevents.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/DimoaCelebrationHall.jpg"),

        ("Herzog Synagogue Hall", "Synagogue Hall", 220, "Center", 32.0830, 34.8000,
         "Modern synagogue hall equipped for religious celebrations, Bar Mitzvahs, and weddings.",
         350.00, 5000.00, 100.00, 0, 1,
         "03-4567890", "herzog@shulhall.example", "https://herzogshul.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/HerzogSyagogueHall.jpg"),

        ("Yokneam Banquet Pavilion", "Banquet Hall", 320, "North", 32.6534, 35.1048,
         "Banquet pavilion with glass walls surrounded by gardens, offering a romantic backdrop for weddings and conferences.",
         950.00, 12500.00, 130.00, 1, 1,
         "04-4567891", "yokneam@pavilion.example", "https://yokneamvenue.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/YokneaBanquetPavilion.jpg"),

        ("Tel Aviv Community Center", "Community Hall", 180, "Center", 32.0700, 34.7800,
         "Modern community center hall designed for both private and public events. Features a spacious stage, adjustable seating, and versatile lighting. The venue is often used for cultural performances, lectures, youth activities, and social celebrations. Its welcoming design and accessible location make it ideal for family gatherings, workshops, and local ceremonies.",
         250.00, 4000.00, 85.00, 1, 1,
         "03-3334444", "events@telavivcc.example", "https://telavivcc.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/TelAvivCommunityCenter.jpg"),

        ("Diamond Wedding Hall", "Wedding Hall", 450, "Center", 32.0800, 34.7800,
         "Prestigious wedding hall with glamorous crystal chandeliers, expansive dance floor, and gourmet catering. Designed for luxury events with state-of-the-art lighting and sound systems. The hall is ideal for weddings, gala events, and upscale receptions.",
         1800.00, 20000.00, 200.00, 1, 1,
         "03-1115555", "diamond@weddinghall.example", "https://diamondweddinghall.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/DiamondWeddngHall.jpg"),

        ("Royal Palace Weddings", "Wedding Hall", 500, "Center", 32.1656, 34.8436,
         "Grand palace-style hall with golden décor, tall ceilings, and a stage for live performances. The venue specializes in large weddings, offering premium catering services, luxurious interiors, and impeccable service. Perfect for extravagant celebrations.",
         2200.00, 25000.00, 240.00, 1, 1,
         "09-8884444", "royal@weddingpalace.example", "https://royalpalace.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/RoyalPalaceWeddings.jpg"),

        ("Sunset Wedding Terrace", "Wedding Hall", 300, "South", 31.5590, 35.4732,
         "Elegant terrace wedding venue with open views of the desert horizon. The space combines indoor elegance with outdoor charm, featuring glass walls, romantic lighting, and full catering options. Ideal for sunset weddings and romantic events.",
         1200.00, 15000.00, 160.00, 1, 1,
         "08-5558888", "sunset@weddingterrace.example", "https://sunsetwedding.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/SunsetWddingTerrace.jpg"),

        ("Jerusalem Crystal Hall", "Wedding Hall", 400, "Jerusalem", 31.7683, 35.2137,
         "A majestic wedding hall in Jerusalem, decorated with crystal lighting and luxurious seating arrangements. This venue is highly regarded for combining traditional Jerusalem atmosphere with modern luxury. Perfect for medium to large-scale weddings.",
         1600.00, 19000.00, 210.00, 1, 1,
         "02-3337777", "crystal@jerusalemhall.example", "https://crystalhall.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/JerusalemCrystalHall.jpg"),

        ("Garden of Dreams Wedding Hall", "Wedding Hall", 350, "North", 32.6996, 35.3035,
         "A wedding hall surrounded by lush gardens and illuminated pathways. The hall offers a mix of indoor luxury and outdoor charm, allowing couples to host both the ceremony and reception in a dreamlike setting. Known for its romantic and enchanting atmosphere.",
         1500.00, 17500.00, 200.00, 1, 1,
         "04-5672222", "dreams@gardenhall.example", "https://gardenhall.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/GardenofDreamsWeddingHall.jpg"),

        ("Tel Aviv Beachside Venue", "Beach Venue", 280, "Center", 32.0809, 34.7806,
         "A vibrant beachside venue directly on the Mediterranean shoreline. Guests enjoy breathtaking sunsets, live music areas, and relaxed seating options. The venue is perfect for weddings, beach parties, and large-scale summer events, combining natural beauty with modern facilities.",
         700.00, 13000.00, None, 0, 0,
         "03-4448888", "beach@telavivvenue.example", "https://tlvbeachvenue.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/TelAvivBeachsideVenue.jpg"),

        ("Sharon Botanical Garden Venue", "Garden", 200, "Center", 32.1600, 34.8400,
         "Garden venue located within a botanical park, offering lush greenery, exotic flowers, and a natural pond. The area is illuminated at night with delicate lights, creating a magical atmosphere for weddings, receptions, and family events.",
         None, 9500.00, 120.00, 1, 1,
         "09-3331111", "sharon@gardenvenue.example", "https://sharongarden.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/SharonBotanicalGardenVenue.jpg"),

        ("Galilee Hills Garden Hall", "Garden", 180, "North", 32.9600, 35.5000,
         "A hillside garden venue overlooking the Galilee, featuring terraced lawns, olive trees, and breathtaking views. The venue is often chosen for rustic-style weddings, open-air concerts, and evening banquets under the stars.",
         None, 8800.00, 110.00, 1, 0,
         "04-8887777", "galilee@gardenhall.example", "https://galileehall.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/GalileeHillsGardenHall.jpg"),

        ("Mediterranean Flavors Restaurant", "Restaurant", 120, "Center", 32.0900, 34.7800,
         "Elegant restaurant venue offering Mediterranean cuisine, a private dining room, and a warm modern décor. Popular for birthdays, business events, and small weddings with a culinary focus.",
         None, None, 150.00, 0, 1,
         "03-5671111", "medflavors@restaurant.example", "https://medflavors.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/MediterraneanFlavorsRestaurant.jpg"),

        ("Galilee Rustic Restaurant", "Restaurant", 90, "North", 32.9650, 35.4950,
         "Rustic restaurant with stone walls, wooden décor, and a charming countryside feel. Known for hosting intimate gatherings, Bar Mitzvahs, and anniversaries with local cuisine and warm service.",
         None, None, 120.00, 0, 1,
         "04-2221111", "galilee@restaurant.example", "https://galileerestaurant.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/GalileeRusticRestaurant.jpg"),

        ("Jerusalem Gourmet Hall", "Restaurant", 140, "Jerusalem", 31.7767, 35.2345,
         "Upscale gourmet restaurant with private event rooms and panoramic views of Jerusalem. Perfect for hosting weddings, corporate dinners, and receptions that combine fine dining with a unique atmosphere.",
         None, None, 200.00, 0, 1,
         "02-7652222", "gourmet@jerusalem.example", "https://jerusalemgourmet.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/JerusalemGourmetHall.jpg"),

        ("Eilat Seaside Grill", "Restaurant", 100, "South", 29.5550, 34.9500,
         "A seaside grill restaurant with a relaxed beach atmosphere. Offers outdoor seating, live music nights, and a menu focused on fresh seafood and grilled specialties. Great for birthdays and seaside weddings.",
         None, None, 160.00, 0, 0,
         "08-9871111", "grill@eilat.example", "https://eilatgrill.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/EilatSeasideGrill.jpg"),

        ("Herzliya Modern Bistro", "Restaurant", 110, "Center", 32.1663, 34.8339,
         "Contemporary bistro with minimalist décor, a wine bar, and an elegant atmosphere. Often chosen for corporate dinners, engagements, and private parties that require a refined yet cozy setting.",
         None, None, 170.00, 0, 1,
         "09-1114444", "bistro@herzliya.example", "https://herzliyabistro.example",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/halls/HerzliyaModernBistro.jpg"),
    ]


    # Insert halls
    for hall in halls:
        (hall_name, hall_type, capacity, region, lat, lon, desc,
         pphour, ppday, ppperson,
         park, wheel, phone, email, website, photo) = hall

        db.execute(
            """INSERT INTO dbo.Hall
               (HallName, HallType, Capacity, Region, Latitude, Longitude, Description,
                PricePerHour, PricePerDay, PricePerPerson,
                ParkingAvailable, WheelchairAccessible,
                ContactPhone, ContactEmail, WebsiteUrl, PhotoUrl)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (hall_name, hall_type, capacity, region, lat, lon, desc,
             pphour, ppday, ppperson, park, wheel, phone, email, website, photo)
        )

    print(f"Bulk data seeding completed successfully with {len(halls)} halls.")


if __name__ == "__main__":
    seed()