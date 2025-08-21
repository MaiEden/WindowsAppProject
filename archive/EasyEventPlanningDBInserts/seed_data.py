"""
seed_data.py
Seed demo data into the Events app database.
50 unique halls with real descriptions and photos.
"""

from datetime import date, time
from server.gateway.DBgateway import *


def seed() -> None:
    db = DbGateway()

    # === Reset existing data ===
    for t in ("EventService", "UserService", "Event", "Hall", "Users"):
        db.execute(f"IF OBJECT_ID('dbo.{t}', 'U') IS NOT NULL DELETE FROM dbo.{t};")

    # === Users ===
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

    # === Map IDs ===
    user_id = {row["Username"]: row["UserId"] for row in db.query("SELECT UserId, Username FROM dbo.Users;")}

    # === Events ===
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

    # === Halls (start of 50) ===
    halls = [
        ("Tel Aviv Loft 22", "Loft", 120, "Center", 32.0853, 34.7818,
         "Industrial-chic loft with high ceilings, urban brick walls, and stylish lighting. Perfect for boutique weddings, private parties, and modern product launches.",
         500.00, None, 120.00, 1, 1,
         "050-1234567", "book@loft22.example", "https://loft22.example",
         "https://images.unsplash.com/photo-1665640622150-0729c9f00adb?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Jerusalem Synagogue Hall", "Synagogue Hall", 200, "Jerusalem", 31.7683, 35.2137,
         "Traditional synagogue hall with wood design and warm lighting. Frequently used for weddings, Bar/Bat Mitzvahs, and community gatherings.",
         420.00, None, 110.00, 0, 1,
         "02-555-1111", "events@synagogue.example", "https://synagogue.example",
         "https://images.unsplash.com/photo-1612388839563-3a6caa5ef4c0?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Haifa Garden Venue", "Garden Venue", 350, "North", 32.7940, 34.9896,
         "Outdoor garden surrounded by waterfalls, green lawns, and romantic lighting. Ideal for large weddings, receptions, and concerts under the stars.",
         None, 10000.00, None, 1, 1,
         "04-9876543", "info@gardenvenue.example", "https://gardenvenue.example",
         "https://plus.unsplash.com/premium_photo-1673569515745-4af4080c95d3?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Herzliya Banquet Center", "Banquet Hall", 500, "Center", 32.1656, 34.8436,
         "Modern banquet hall with LED lighting, spacious stage, and central dance floor. Great for weddings, conferences, and formal galas.",
         1200.00, 15000.00, 150.00, 1, 1,
         "09-1234567", "sales@banquetcenter.example", "https://banquetcenter.example",
         "https://images.unsplash.com/photo-1677129663241-5be1f17fe6fe?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Dead Sea Hotel Ballroom", "Hotel Ballroom", 400, "South", 31.5590, 35.4732,
         "Luxurious ballroom with chandeliers, sea views, and full catering. Popular for destination weddings, retreats, and elegant dinners.",
         2000.00, 20000.00, 180.00, 1, 1,
         "08-7654321", "events@hotelballroom.example", "https://hotelballroom.example",
         "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c"),


        ("Golan Heights Banquet Hall", "Banquet Hall", 280, "North", 32.9925, 35.6900,
         "Spacious banquet hall in the Golan, surrounded by scenic views. Designed for weddings, Bar/Bat Mitzvahs, and corporate events.",
         700.00, 8000.00, 140.00, 1, 0,
         "04-5551212", "events@golanbanquet.example", "https://golanbanquet.example",
         "https://images.unsplash.com/photo-1588963200960-44cf8e2b6fed?q=80&w=1925&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Ashdod Event Hall", "Event Hall", 600, "South", 31.8014, 34.6435,
         "Modern event hall with industrial design and flexible seating arrangements. Popular for weddings, exhibitions, and concerts.",
         1000.00, 12000.00, 100.00, 1, 0,
         "08-9990000", "info@ashdodevent.example", "https://ashdodevent.example",
         "https://images.unsplash.com/photo-1665607437981-973dcd6a22bb?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Caesarea Luxury Villa", "Villa", 100, "Center", 32.5000, 34.9000,
         "Exclusive villa with a pool, beachfront access, and elegant design. Ideal for boutique weddings and private retreats.",
         1500.00, 18000.00, 250.00, 1, 1,
         "054-1112233", "villa@luxury.example", "https://luxuryvilla.example",
         "https://images.unsplash.com/photo-1600585154340-be6161a56a0c"),

        ("Herzliya Restaurant Venue", "Restaurant Venue", 200, "Center", 32.1656, 34.8436,
         "Fine-dining restaurant venue with private rooms and outdoor seating. Perfect for birthdays, anniversaries, and intimate weddings.",
         900.00, 10000.00, 140.00, 1, 1,
         "09-4445555", "dining@herzliya.example", "https://herzrestaurant.example",
         "https://images.unsplash.com/photo-1498654896293-37aacf113fd9"),

        ("Zichron Banquet Hall", "Banquet Hall", 350, "North", 32.5667, 34.9500,
         "Banquet hall located in Zichron Yaakov, surrounded by greenery. Designed for weddings, large dinners, and family celebrations.",
         950.00, 11000.00, 150.00, 1, 1,
         "04-1239876", "zichron@banquethall.example", "https://zichronbanquet.example",
         "https://images.unsplash.com/photo-1632316962873-47ee3d309f02?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDF8fHxlbnwwfHx8fHw%3D"),
    ]
    halls += [
        ("Bat Yam Event Loft", "Loft", 90, "Center", 32.0230, 34.7519,
         "Modern loft with floor-to-ceiling windows and minimalist décor. Perfect for birthdays, cocktail events, and private parties.",
         400.00, 5000.00, 80.00, 0, 1,
         "03-1112222", "loft@batyamevents.example", "https://batyamevents.example",
         "https://planner5d.com/blog/content/images/2024/01/game-room-ideas.jpg"),

        ("Eilat Beach Club", "Beach Venue", 300, "South", 29.5577, 34.9519,
         "Vibrant beach venue with stage, cocktail bar, and direct sea access. Ideal for concerts, weddings, and summer celebrations.",
         600.00, 15000.00, None, 0, 0,
         "08-2224444", "info@beachclub.example", "https://beachclub.example",
         "https://images.unsplash.com/photo-1608956905586-adaad6346779?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Petah Tikva Grand Banquet", "Banquet Hall", 480, "Center", 32.0918, 34.8850,
         "Large banquet hall with LED walls, premium sound, and spacious dance floor. Designed for weddings and galas.",
         1100.00, 14000.00, 140.00, 1, 1,
         "03-8889999", "grand@banquetptk.example", "https://banquetptk.example",
         "https://images.unsplash.com/photo-1686853020996-f9634bcca921?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Nazareth Olive Garden Venue", "Garden Venue", 220, "North", 32.6996, 35.3035,
         "Romantic olive garden with outdoor dining and string lighting. Popular for weddings, receptions, and private events.",
         None, 6000.00, 90.00, 1, 0,
         "04-7654321", "garden@nazareth.example", "https://nazarethgarden.example",
         "https://images.unsplash.com/photo-1470770841072-f978cf4d019e"),

        ("Beer Sheva Cultural Center", "Event Hall", 350, "South", 31.2520, 34.7915,
         "Spacious event hall with a stage and exhibition space. Frequently used for weddings, concerts, and community gatherings.",
         500.00, 7000.00, 120.00, 1, 1,
         "08-3334444", "culture@beersheva.example", "https://beershevacenter.example",
         "https://www.matnas-betel.org.il/productImages2/88/2023/06/13/image1686639501.jpg"),

        ("Holon Modern Loft", "Loft", 110, "Center", 32.0158, 34.7874,
         "Contemporary loft with exposed brick and open plan. Popular for private parties, launches, and creative events.",
         450.00, 5500.00, 85.00, 1, 1,
         "03-2223333", "holon@modernloft.example", "https://holonloft.example",
         "https://wp-media-partyslate.imgix.net/2021/01/photo-69eb053e-12cc-4fb9-bf56-ed097675693f.jpg?auto=compress%2Cformat&ixlib=php-3.3.1"),

        ("Tiberias Lake Ballroom", "Hotel Ballroom", 270, "North", 32.7959, 35.5313,
         "Elegant ballroom with stunning views of the Sea of Galilee. A top choice for weddings and luxury celebrations.",
         900.00, 12000.00, 150.00, 1, 1,
         "04-1119999", "lake@tiberiasvenue.example", "https://tiberiasvenue.example",
         "https://images.unsplash.com/photo-1647451276551-3556064b252c?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDF8fHxlbnwwfHx8fHw%3D")
    ]
    halls += [
        ("Rosh Pina Garden Villa", "Villa", 90, "North", 32.9680, 35.5427,
         "Charming villa surrounded by greenery, featuring an intimate pool area and spacious garden. Great for boutique weddings and private celebrations.",
         850.00, 9500.00, 160.00, 1, 1,
         "04-1122334", "villa@roshpina.example", "https://roshpinavilla.example",
         "https://images.unsplash.com/photo-1512917774080-9991f1c4c750"),

        ("Kiryat Gat Synagogue Hall", "Synagogue Hall", 180, "South", 31.6100, 34.7650,
         "Spacious synagogue hall designed for Bar Mitzvahs, weddings, and community events. Includes updated seating and stage.",
         300.00, 4000.00, 80.00, 0, 1,
         "08-5671234", "synagogue@kiryatgat.example", "https://kiryatgatshul.example",
         "https://plus.unsplash.com/premium_photo-1673626582397-0bcb43707f44?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Modiin Event Center", "Banquet Hall", 420, "Center", 31.8928, 35.0119,
         "Modern banquet hall with customizable seating, advanced lighting, and professional catering services. Perfect for large weddings and galas.",
         1300.00, 16000.00, 145.00, 1, 1,
         "08-3216549", "modiin@eventcenter.example", "https://modiineventcenter.example",
         "https://images.unsplash.com/photo-1679452233226-8810221cec3a?q=80&w=871&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Ashkelon Coastal Venue", "Garden Venue", 240, "South", 31.6688, 34.5715,
         "Coastal garden with cabanas, live music stage, and romantic lighting. Designed for weddings and seaside events.",
         650.00, 11000.00, None, 0, 0,
         "08-3219987", "coastal@ashkelon.example", "https://ashkelonvenue.example",
         "https://plus.unsplash.com/premium_photo-1661775263105-57b126d6bb4e?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Herzliya Marina Ballroom", "Hotel Ballroom", 220, "Center", 32.1656, 34.8436,
         "Elegant ballroom overlooking the marina, offering luxurious décor and catering. Suitable for weddings and formal dinners.",
         2000.00, 18000.00, 280.00, 1, 1,
         "09-9988776", "yacht@herzliya.example", "https://herzliyayacht.example",
         "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?q=80&w=898&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Tel Aviv Seaside Ballroom", "Banquet Hall", 380, "Center", 32.0809, 34.7806,
         "High-end ballroom with sea view terraces, crystal chandeliers, and full-service catering. Ideal for luxury weddings.",
         1800.00, 19000.00, 220.00, 1, 1,
         "03-2225555", "seaside@ballroom.example", "https://seasideballroom.example",
         "https://images.unsplash.com/photo-1608538242744-5ba626320a67?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Dimona Celebration Hall", "Event Hall", 280, "South", 31.0700, 35.0300,
         "Modern celebration hall with large stage, professional lighting, and dance floor. Frequently used for weddings and corporate events.",
         400.00, 6000.00, 95.00, 1, 1,
         "08-6782345", "dimona@celebration.example", "https://dimonaevents.example",
         "https://images.unsplash.com/photo-1733244738988-70b1f4b96c37?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Herzog Synagogue Hall", "Synagogue Hall", 220, "Center", 32.0830, 34.8000,
         "Modern synagogue hall equipped for religious celebrations, Bar Mitzvahs, and weddings.",
         350.00, 5000.00, 100.00, 0, 1,
         "03-4567890", "herzog@shulhall.example", "https://herzogshul.example",
         "https://plus.unsplash.com/premium_photo-1673626581283-2f3723c9d698?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Yokneam Banquet Pavilion", "Banquet Hall", 320, "North", 32.6534, 35.1048,
         "Banquet pavilion with glass walls surrounded by gardens, offering a romantic backdrop for weddings and conferences.",
         950.00, 12500.00, 130.00, 1, 1,
         "04-4567891", "yokneam@pavilion.example", "https://yokneamvenue.example",
         "https://images.unsplash.com/photo-1524824267900-2fa9cbf7a506?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Tel Aviv Community Center", "Community Hall", 180, "Center", 32.0700, 34.7800,
         "Modern community center hall designed for both private and public events. Features a spacious stage, adjustable seating, and versatile lighting. The venue is often used for cultural performances, lectures, youth activities, and social celebrations. Its welcoming design and accessible location make it ideal for family gatherings, workshops, and local ceremonies.",
         250.00, 4000.00, 85.00, 1, 1,
         "03-3334444", "events@telavivcc.example", "https://telavivcc.example",
         "https://www.matnas-betel.org.il/productImages2/88/2024/03/27/image1711524247.jpg"),

        ("Diamond Wedding Hall", "Wedding Hall", 450, "Center", 32.0800, 34.7800,
         "Prestigious wedding hall with glamorous crystal chandeliers, expansive dance floor, and gourmet catering. Designed for luxury events with state-of-the-art lighting and sound systems. The hall is ideal for weddings, gala events, and upscale receptions.",
         1800.00, 20000.00, 200.00, 1, 1,
         "03-1115555", "diamond@weddinghall.example", "https://diamondweddinghall.example",
         "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?q=80&w=898&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Royal Palace Weddings", "Wedding Hall", 500, "Center", 32.1656, 34.8436,
         "Grand palace-style hall with golden décor, tall ceilings, and a stage for live performances. The venue specializes in large weddings, offering premium catering services, luxurious interiors, and impeccable service. Perfect for extravagant celebrations.",
         2200.00, 25000.00, 240.00, 1, 1,
         "09-8884444", "royal@weddingpalace.example", "https://royalpalace.example",
         "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c"),

        ("Sunset Wedding Terrace", "Wedding Hall", 300, "South", 31.5590, 35.4732,
         "Elegant terrace wedding venue with open views of the desert horizon. The space combines indoor elegance with outdoor charm, featuring glass walls, romantic lighting, and full catering options. Ideal for sunset weddings and romantic events.",
         1200.00, 15000.00, 160.00, 1, 1,
         "08-5558888", "sunset@weddingterrace.example", "https://sunsetwedding.example",
         "https://images.unsplash.com/photo-1524824267900-2fa9cbf7a506?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"),

        ("Jerusalem Crystal Hall", "Wedding Hall", 400, "Jerusalem", 31.7683, 35.2137,
         "A majestic wedding hall in Jerusalem, decorated with crystal lighting and luxurious seating arrangements. This venue is highly regarded for combining traditional Jerusalem atmosphere with modern luxury. Perfect for medium to large-scale weddings.",
         1600.00, 19000.00, 210.00, 1, 1,
         "02-3337777", "crystal@jerusalemhall.example", "https://crystalhall.example",
         "https://images.unsplash.com/photo-1724855946379-451f59d45df6"),

        ("Garden of Dreams Wedding Hall", "Wedding Hall", 350, "North", 32.6996, 35.3035,
         "A wedding hall surrounded by lush gardens and illuminated pathways. The hall offers a mix of indoor luxury and outdoor charm, allowing couples to host both the ceremony and reception in a dreamlike setting. Known for its romantic and enchanting atmosphere.",
         1500.00, 17500.00, 200.00, 1, 1,
         "04-5672222", "dreams@gardenhall.example", "https://gardenhall.example",
         "https://images.unsplash.com/photo-1578298880489-ff269cea9894"),

        ("Tel Aviv Beachside Venue", "Beach Venue", 280, "Center", 32.0809, 34.7806,
         "A vibrant beachside venue directly on the Mediterranean shoreline. Guests enjoy breathtaking sunsets, live music areas, and relaxed seating options. The venue is perfect for weddings, beach parties, and large-scale summer events, combining natural beauty with modern facilities.",
         700.00, 13000.00, None, 0, 0,
         "03-4448888", "beach@telavivvenue.example", "https://tlvbeachvenue.example",
         "https://plus.unsplash.com/premium_photo-1674252314224-bbcbf0703150"),

        ("Sharon Botanical Garden Venue", "Garden", 200, "Center", 32.1600, 34.8400,
         "Garden venue located within a botanical park, offering lush greenery, exotic flowers, and a natural pond. The area is illuminated at night with delicate lights, creating a magical atmosphere for weddings, receptions, and family events.",
         None, 9500.00, 120.00, 1, 1,
         "09-3331111", "sharon@gardenvenue.example", "https://sharongarden.example",
         "https://plus.unsplash.com/premium_photo-1676302451098-189ebe35cc3a"),

        ("Galilee Hills Garden Hall", "Garden", 180, "North", 32.9600, 35.5000,
         "A hillside garden venue overlooking the Galilee, featuring terraced lawns, olive trees, and breathtaking views. The venue is often chosen for rustic-style weddings, open-air concerts, and evening banquets under the stars.",
         None, 8800.00, 110.00, 1, 0,
         "04-8887777", "galilee@gardenhall.example", "https://galileehall.example",
         "https://plus.unsplash.com/premium_photo-1661775263105-57b126d6bb4e"),

        ("Mediterranean Flavors Restaurant", "Restaurant", 120, "Center", 32.0900, 34.7800,
         "Elegant restaurant venue offering Mediterranean cuisine, a private dining room, and a warm modern décor. Popular for birthdays, business events, and small weddings with a culinary focus.",
         None, None, 150.00, 0, 1,
         "03-5671111", "medflavors@restaurant.example", "https://medflavors.example",
         "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4"),

        ("Galilee Rustic Restaurant", "Restaurant", 90, "North", 32.9650, 35.4950,
         "Rustic restaurant with stone walls, wooden décor, and a charming countryside feel. Known for hosting intimate gatherings, Bar Mitzvahs, and anniversaries with local cuisine and warm service.",
         None, None, 120.00, 0, 1,
         "04-2221111", "galilee@restaurant.example", "https://galileerestaurant.example",
         "https://images.unsplash.com/photo-1667388969250-1c7220bf3f37"),

        ("Jerusalem Gourmet Hall", "Restaurant", 140, "Jerusalem", 31.7767, 35.2345,
         "Upscale gourmet restaurant with private event rooms and panoramic views of Jerusalem. Perfect for hosting weddings, corporate dinners, and receptions that combine fine dining with a unique atmosphere.",
         None, None, 200.00, 0, 1,
         "02-7652222", "gourmet@jerusalem.example", "https://jerusalemgourmet.example",
         "https://images.unsplash.com/photo-1528605248644-14dd04022da1"),

        ("Eilat Seaside Grill", "Restaurant", 100, "South", 29.5550, 34.9500,
         "A seaside grill restaurant with a relaxed beach atmosphere. Offers outdoor seating, live music nights, and a menu focused on fresh seafood and grilled specialties. Great for birthdays and seaside weddings.",
         None, None, 160.00, 0, 0,
         "08-9871111", "grill@eilat.example", "https://eilatgrill.example",
         "https://images.unsplash.com/photo-1617079114138-9cf245e006c4"),

        ("Herzliya Modern Bistro", "Restaurant", 110, "Center", 32.1663, 34.8339,
         "Contemporary bistro with minimalist décor, a wine bar, and an elegant atmosphere. Often chosen for corporate dinners, engagements, and private parties that require a refined yet cozy setting.",
         None, None, 170.00, 0, 1,
         "09-1114444", "bistro@herzliya.example", "https://herzliyabistro.example",
         "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4"),


    ]



    # === Insert into DB ===
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

    print(f"✅ Bulk data seeding completed successfully with {len(halls)} halls.")


if __name__ == "__main__":
    seed()