"""
Seeds decoration options into the Events app database (dbo.DecorOption).

What this script does:
- Clears existing rows from DecorOption.
- Inserts a diverse demo catalog of decoration options (balloons, flowers, linens, lighting, etc.)
  with English content, realistic pricing (small/medium/large), regions across Israel,
  vendor contact details, and operational fields (setup/teardown, availability, lead time).
"""
from server.gateway.DBgateway import DbGateway

def seed() -> None:
    """
    Populate dbo.DecorOption with deterministic demo data.

    Steps:
      1) Wipe existing data.
      2) Insert catalog that covers many categories and regions.
    """
    db = DbGateway()

    # 1) Wipe existing rows
    db.execute("IF OBJECT_ID('dbo.DecorOption', 'U') IS NOT NULL DELETE FROM dbo.DecorOption;")

    # 2) Demo catalog (≥ 36 rows; English content; varied categories & regions)
    # Column order must match the INSERT below.
    decor = [
        # --- Balloons (multiple regions) ---
        ("Balloons – Classic Arch", "Balloons", "Classic",
         "Balloon arch for entrances or stages; includes installation and safe anchoring.",
         1, 0, 60, 30, 350.00, 690.00, 990.00, 120.00,
         "Center", "BalloonArt", "+972-52-1112233", "info@balloonart.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Balloons%E2%80%93ClassicArch.jpg", 5,
         "Free cancellation up to 7 days before event.", 1),

        ("Balloons – Colorful Columns", "Balloons", "Colorful Party",
         "Pair of balloon columns (2.2m) with a vibrant top sphere, great for birthdays.",
         1, 0, 45, 25, 280.00, 560.00, 840.00, 90.00,
         "North", "EventMagic", "+972-54-9988776", "contact@eventmagic.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Balloons%E2%80%93ColorfulColumns.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        ("Balloons – Organic Garland", "Balloons", "Modern Minimalist",
         "Organic balloon garland along a backdrop or railing; matte pastel tones available.",
         1, 0, 75, 35, 420.00, 780.00, 1190.00, 140.00,
         "Jerusalem", "DecoPro", "+972-50-4455667", "orders@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Balloons%E2%80%93OrganicGarland.jpg", 7,
         "Free cancellation up to 7 days before event.", 1),

        ("Balloons – Neon Glow Set", "Balloons", "Bold Neon",
         "UV-reactive balloon set for club-style effects; includes glow accents.",
         1, 0, 70, 30, 480.00, 890.00, 1290.00, 130.00,
         "South", "ShinyEvents", "+972-53-2345678", "team@shinyevents.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Balloons%E2%80%93NeonGlowSet.jpg", 6,
         "Free cancellation up to 7 days before event.", 1),

        # --- Flowers ---
        ("Floral Centerpieces – Roses & Eucalyptus", "Flowers", "Romantic Red Roses",
         "Set of elegant table centerpieces with roses, eucalyptus, and seasonal greens.",
         1, 0, 50, 25, 520.00, 980.00, 1450.00, 110.00,
         "Center", "BloomDesigns", "+972-52-5566778", "studio@bloomdesigns.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/FloralCenterpieces%E2%80%93Roses&Eucalyptus.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Floral Runner – Rustic Olive & Gypsophila", "Flowers", "Rustic Wood Greenery",
         "Long floral runner for head table; rustic style with olive branches and gypsophila.",
         1, 0, 65, 30, 590.00, 1090.00, 1590.00, 120.00,
         "Galilee", "BloomDesigns", "+972-52-6677889", "hello@bloomdesigns.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/FloraRunner%E2%80%93RusticOlive&Gypsophila.jpg", 6,
         "Free cancellation up to 7 days before event.", 1),

        ("Floral Backdrop – Pastel Garden Wall", "Flowers", "Pastel Soft",
         "Pastel-toned faux flower wall for photos; reusable panels with lush look.",
         1, 0, 80, 40, 780.00, 1290.00, 1790.00, 160.00,
         "Jerusalem", "EventMagic", "+972-54-2233445", "sales@eventmagic.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/FloralBackdrop%E2%80%93PastelGardenWall.jpg", 8,
         "Free cancellation up to 7 days before event.", 1),

        # --- Tableware ---
        ("Decorative Tableware – Gold Rim Set", "Tableware", "Elegant Black Tie",
         "Disposable plates and cups with gold rim, matching cutlery, and napkins.",
         1, 0, 35, 20, 240.00, 440.00, 690.00, 80.00,
         "Center", "DecoPro", "+972-50-9988775", "orders@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/DecorativeTableware%E2%80%93GoldRimSet.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        ("Decorative Tableware – Mediterranean Blue", "Tableware", "Nature Inspired",
         "Patterned disposable tableware set in blue tones, ideal for seaside themes.",
         1, 0, 35, 20, 210.00, 390.00, 640.00, 80.00,
         "Sharon", "DecoPro", "+972-50-1122334", "hello@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/DecorativeTableware%E2%80%93MediterraneanBlue.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        # --- Linens ---
        ("Linens – Ivory Tablecloth & Napkins", "Linens", "Classic White Gold",
         "Premium polyester linens (ivory) with matching napkins; wrinkle-resistant.",
         1, 0, 40, 20, 320.00, 620.00, 920.00, 90.00,
         "Center", "EliteLinens", "+972-58-4455667", "service@elitelinens.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Linens%E2%80%93IvoryTablecloth&Napkins.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Linens – Black Tie Set", "Linens", "Elegant Black Tie",
         "Black tablecloths with satin napkins for formal atmospheres.",
         1, 0, 40, 20, 340.00, 650.00, 950.00, 90.00,
         "Jerusalem", "EliteLinens", "+972-58-5566778", "orders@elitelinens.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Linens%E2%80%93BlackTieSet.jpg", 5,
         "Free cancellation up to 7 days before event.", 1),

        # --- Lighting ---
        ("Ambient String Lights", "Lighting", "Vintage Style",
         "Warm string lights for cozy ambiance; includes safe cable management.",
         1, 1, 60, 30, 360.00, 690.00, 1090.00, 120.00,
         "North", "GlowLighting", "+972-53-1234567", "info@glowlighting.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/AmbientStringLights.jpg", 7,
         "Free cancellation up to 7 days before event.", 1),

        ("Stage Uplights Package", "Lighting", "Modern Minimalist",
         "LED uplights for walls and stage; DMX-controlled static color selection.",
         1, 1, 70, 35, 420.00, 820.00, 1290.00, 140.00,
         "Center", "GlowLighting", "+972-53-2345678", "sales@glowlighting.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/StageUplightsPackage.jpg", 7,
         "Free cancellation up to 7 days before event.", 1),

        ("Fairy Lights Canopy", "Lighting", "Romantic",
         "Dense fairy-light canopy over dance floor or garden path; magical effect.",
         1, 1, 90, 45, 520.00, 990.00, 1490.00, 160.00,
         "South", "GlowLighting", "+972-53-3456789", "team@glowlighting.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/FairyLightsCanopy.jpg", 8,
         "Free cancellation up to 7 days before event.", 1),

        # --- Backdrop ---
        ("Backdrop – Velvet Curtain Wall", "Backdrop", "Luxury Glam",
         "Free-standing velvet curtain wall for photo ops; includes pipe & drape.",
         1, 0, 60, 30, 450.00, 820.00, 1190.00, 130.00,
         "Jerusalem", "BackdropStudio", "+972-52-3344556", "hello@backdropstudio.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Backdrop%E2%80%93VelvetCurtainWall.jpg", 6,
         "Free cancellation up to 7 days before event.", 1),

        ("Backdrop – Greenery Panel", "Backdrop", "Nature Inspired",
         "Modular greenery panels (faux) forming a lush photo wall.",
         1, 0, 65, 30, 480.00, 890.00, 1290.00, 140.00,
         "Sharon", "BackdropStudio", "+972-52-9988776", "orders@backdropstudio.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Backdrop%E2%80%93GreeneryPanel.jpg", 6,
         "Free cancellation up to 7 days before event.", 1),

        # --- CakeStands ---
        ("Cake Stands – Marble & Gold Set", "CakeStands", "Luxury Glam",
         "Marble-pattern stands with gold accents; multi-height dessert display.",
         1, 0, 35, 20, 250.00, 460.00, 720.00, 70.00,
         "Center", "SweetStands", "+972-55-1122334", "info@sweetstands.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/CakeStands%E2%80%93Marble&GoldSet.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        ("Cake Stands – Rustic Wood Trio", "CakeStands", "Rustic Wood Greenery",
         "Solid wood stands (S/M/L) with natural finish; great for outdoor themes.",
         1, 0, 35, 20, 230.00, 430.00, 690.00, 70.00,
         "North", "SweetStands", "+972-55-2233445", "orders@sweetstands.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/CakeStands%E2%80%93RusticWoodTrio.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        # --- Props ---
        ("Props – Vintage Suitcase Corner", "Props", "Vintage Style",
         "Decor corner with stacked vintage suitcases, lantern, and lace accents.",
         1, 0, 40, 20, 260.00, 490.00, 760.00, 80.00,
         "Galilee", "PropMasters", "+972-57-5566778", "props@propmasters.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Props%E2%80%93VintageSuitcaseCorner.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Props – Tropical Bar Set", "Props", "Tropical Vibes",
         "Bamboo-style bar front with palm props; optional faux fruit crates.",
         1, 0, 55, 25, 340.00, 640.00, 980.00, 110.00,
         "South", "PropMasters", "+972-57-6677889", "team@propmasters.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Props%E2%80%93TropicalBarSet.jpg", 5,
         "Free cancellation up to 7 days before event.", 1),

        # --- Centerpieces ---
        ("Centerpieces – Candles & Mirrors", "Centerpieces", "Modern Minimalist",
         "Mirror base with mixed-height candles and greenery rings.",
         1, 0, 35, 20, 300.00, 560.00, 890.00, 90.00,
         "Center", "DecoPro", "+972-50-2233445", "service@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Centerpieces%E2%80%93Candles&Mirrors.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Centerpieces – Lantern & Olive", "Centerpieces", "Rustic Wood Greenery",
         "Metal lantern centerpiece with olive branch accents; warm, rustic mood.",
         1, 0, 40, 20, 320.00, 590.00, 920.00, 90.00,
         "Jerusalem", "DecoPro", "+972-50-3344556", "orders@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Centerpieces%E2%80%93Lantern&Olive.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        # --- Signage ---
        ("Signage – Welcome Board (Acrylic)", "Signage", "Modern Minimalist",
         "Frosted acrylic welcome sign with custom lettering; easel included.",
         1, 0, 25, 15, 200.00, 360.00, 520.00, 60.00,
         "Center", "DecoPro", "+972-50-7788991", "design@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Signage%E2%80%93WelcomeBoardAcrylic.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        ("Signage – Seating Plan Board", "Signage", "Elegant Black Tie",
         "Printed seating chart on foam board with gold frame; stylish and clear.",
         1, 0, 30, 15, 220.00, 380.00, 540.00, 60.00,
         "Sharon", "DecoPro", "+972-50-8899002", "print@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Signage%E2%80%93SeatingPlanBoard.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        # --- Extra coverage for regions/categories ---
        ("Backdrop – Fabric Arched Frame", "Backdrop", "Classic White Gold",
         "Arched metal frame with fabric drape; simple and elegant photo corner.",
         1, 0, 55, 25, 380.00, 720.00, 1080.00, 120.00,
         "North", "BackdropStudio", "+972-52-4455667", "studio@backdropstudio.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Backdrop%E2%80%93FabricArchedFrame.jpg", 6,
         "Free cancellation up to 7 days before event.", 1),

        ("Lighting – Bistro Bulbs Lines", "Lighting", "Vintage Style",
         "Overhead bistro bulb lines for outdoor patios or indoor halls.",
         1, 1, 60, 30, 370.00, 710.00, 1120.00, 130.00,
         "Center", "GlowLighting", "+972-53-7788990", "bistro@glowlighting.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Lighting%E2%80%93BistroBulbsLines.jpg", 7,
         "Free cancellation up to 7 days before event.", 1),

        ("Linens – Pastel Mix", "Linens", "Pastel Soft",
         "Soft pastel tablecloth set with matching napkins; spring vibe.",
         1, 0, 40, 20, 330.00, 640.00, 950.00, 90.00,
         "Galilee", "EliteLinens", "+972-58-6677889", "pastel@elitelinens.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Linens%E2%80%93PastelMix.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Props – Photo Booth Corner", "Props", "Modern Minimalist",
         "Backdrop stand, simple props, and lighting for a pop-up photo booth.",
         1, 1, 50, 25, 360.00, 690.00, 1050.00, 120.00,
         "Jerusalem", "PropMasters", "+972-57-7788990", "photo@propmasters.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Props%E2%80%93PhotoBoothCorner.jpg", 5,
         "Free cancellation up to 7 days before event.", 1),

        ("Centerpieces – Green Bottles & Stems", "Centerpieces", "Nature Inspired",
         "Glass bottles with single-stem flowers and greenery; minimal & chic.",
         1, 0, 30, 15, 260.00, 480.00, 760.00, 80.00,
         "Sharon", "DecoPro", "+972-50-9911223", "center@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Centerpieces%E2%80%93GreenBottles&Stems.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        ("Tableware – Black Matte Set", "Tableware", "Modern Minimalist",
         "Matte black disposable plates and cutlery; contemporary event style.",
         1, 0, 35, 20, 260.00, 490.00, 740.00, 80.00,
         "South", "DecoPro", "+972-50-8811223", "modern@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Tableware%E2%80%93BlackMatteSet.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        ("Flowers – White Hydrangea Towers", "Flowers", "Classic White Gold",
         "Tall hydrangea arrangements for stage sides or entryway.",
         1, 0, 75, 35, 720.00, 1190.00, 1690.00, 150.00,
         "Jerusalem", "BloomDesigns", "+972-52-7788990", "stage@bloomdesigns.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Flowers%E2%80%93WhiteHydrangeaTowers.jpg", 7,
         "Free cancellation up to 7 days before event.", 1),

        ("Balloons – Pastel Columns with Numbers", "Balloons", "Pastel Soft",
         "Two pastel balloon columns with large number balloons; birthdays & milestones.",
         1, 0, 50, 25, 300.00, 560.00, 820.00, 90.00,
         "Center", "BalloonArt", "+972-52-3344556", "pastel@balloonart.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Balloons%E2%80%93PastelColumnswithNumbers.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Signage – Table Numbers (Acrylic)", "Signage", "Modern Minimalist",
         "Set of acrylic table numbers with clear stand; sleek look.",
         1, 0, 20, 15, 180.00, 320.00, 480.00, 60.00,
         "Center", "DecoPro", "+972-50-6677889", "tables@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Signage%E2%80%93TableNumbers(Acrylic).jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        ("Backdrop – Neon Sign Wall", "Backdrop", "Bold Neon",
         "Custom neon wording mounted on a greenery or matte board wall.",
         1, 1, 85, 40, 820.00, 1290.00, 1780.00, 170.00,
         "South", "BackdropStudio", "+972-52-7711223", "neon@backdropstudio.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Backdrop%E2%80%93NeonSignWal.jpg", 8,
         "Free cancellation up to 7 days before event.", 1),

        ("Lighting – Monogram Projector", "Lighting", "Luxury Glam",
         "Personalized monogram projection on dance floor or wall; technician included.",
         1, 1, 70, 35, 520.00, 940.00, 1390.00, 140.00,
         "Center", "GlowLighting", "+972-53-9911223", "mono@glowlighting.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Lighting%E2%80%93MonogramProjector.jpg", 7,
         "Free cancellation up to 7 days before event.", 1),

        ("Linens – Lace Overlays", "Linens", "Vintage Style",
         "Lace overlays for round tables; adds texture and vintage elegance.",
         1, 0, 45, 20, 300.00, 560.00, 880.00, 90.00,
         "North", "EliteLinens", "+972-58-7711223", "lace@elitelinens.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Linens%E2%80%93LaceOverlays.jpg", 5,
         "Free cancellation up to 7 days before event.", 1),

        ("Cake Stands – Mirror & Crystal", "CakeStands", "Luxury Glam",
         "Mirrored cake stand with crystal accents; premium dessert presentation.",
         1, 0, 35, 20, 280.00, 520.00, 780.00, 70.00,
         "Jerusalem", "SweetStands", "+972-55-9911223", "mirror@sweetstands.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/CakeStands%E2%80%93Mirror&Crystal.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Props – Kids Party Set", "Props", "Colorful Party",
         "Fun props bundle with banners, paper fans, and themed cutouts.",
         1, 0, 40, 20, 240.00, 450.00, 690.00, 70.00,
         "Sharon", "PropMasters", "+972-57-9911223", "kids@propmasters.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Props%E2%80%93KidsPartySet.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Centerpieces – Floating Candles", "Centerpieces", "Romantic",
         "Glass cylinders with floating candles and greenery; soft romantic light.",
         1, 0, 35, 20, 280.00, 520.00, 820.00, 80.00,
         "South", "DecoPro", "+972-50-7733445", "float@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Centerpieces%E2%80%93FloatingCandles.jpg", 4,
         "Free cancellation up to 7 days before event.", 1),

        ("Signage – Directional Arrows", "Signage", "Modern Minimalist",
         "Directional sign set for guiding guests between areas (ceremony, dinner, dance).",
         1, 0, 25, 15, 190.00, 330.00, 490.00, 60.00,
         "Galilee", "DecoPro", "+972-50-6611223", "signs@decopro.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Signage%E2%80%93DirectionalArrows.jpg", 3,
         "Free cancellation up to 7 days before event.", 1),

        ("Balloons – Heart Backdrop", "Balloons", "Romantic",
         "Heart-shaped balloon backdrop; popular for engagements and anniversaries.",
         1, 0, 60, 30, 380.00, 720.00, 1060.00, 120.00,
         "Jerusalem", "BalloonArt", "+972-52-7711333", "hearts@balloonart.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Balloons%E2%80%93HeartBackdrop.jpg", 6,
         "Free cancellation up to 7 days before event.", 1),

        ("Flowers – Tropical Centerpieces", "Flowers", "Tropical Vibes",
         "Centerpieces with monstera leaves, orchids, and pineapple accents (non-edible).",
         1, 0, 55, 25, 540.00, 990.00, 1490.00, 130.00,
         "Center", "BloomDesigns", "+972-52-6611444", "tropical@bloomdesigns.com",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/decor/Flowers%E2%80%93TropicalCenterpieces.jpg", 6,
         "Free cancellation up to 7 days before event.", 1),
    ]

    # Insert
    db.execute_many(
        """
        INSERT INTO dbo.DecorOption
            (DecorName, Category, Theme, Description,
             Indoor, RequiresElectricity, SetupDurationMinutes, TeardownDurationMinutes,
             PriceSmall, PriceMedium, PriceLarge, DeliveryFee,
             Region, VendorName, ContactPhone, ContactEmail, PhotoUrl,
             LeadTimeDays, CancellationPolicy, Available)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        decor
    )

    print(f"Decor seeding completed successfully with {len(decor)} records.")


if __name__ == "__main__":
    seed()
