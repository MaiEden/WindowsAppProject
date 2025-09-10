"""
Seeds service options (activities/entertainment/workshops/music/shows/kids/speaker/games)
into the Events app database (dbo.ServiceOption).

What this script does:
- Clears existing rows from ServiceOption.
- Inserts a diverse demo catalog of 40 services with long, realistic descriptions,
  regions across Israel, vendor contact info, operational flags, and pricing
  (base price + price per person).
"""
from server.gateway.DBgateway import DbGateway


def seed() -> None:
    """
    Populate dbo.ServiceOption with deterministic demo data.

    Steps:
      1) Wipe existing data.
      2) Insert catalog that covers many categories and regions.
    """
    db = DbGateway()

    # 1) Wipe existing rows
    db.execute("IF OBJECT_ID('dbo.ServiceOption', 'U') IS NOT NULL DELETE FROM dbo.ServiceOption;")

    # 2) Demo catalog (40 rows)
    # Column order must match the INSERT below.
    # (
    #   ServiceName, Category, Subcategory, ShortDescription, Description, PhotoUrl,
    #   MinAge, MaxAge, MinParticipants, MaxParticipants,
    #   IsOutdoor, NoiseLevel, StageRequired, RequiresElectricity,
    #   Region, TravelLimitKm, TravelFeeBase, TravelFeePerKm,
    #   VendorName, ContactPhone, ContactEmail,
    #   BasePrice, PricePerPerson, LeadTimeDays, CancellationPolicy, Available
    # )
    services = [
        # --- Entertainment / Shows ---
        ("Stand-up Comedy Night", "Show", "Standup",
         "Evening stand‑up set tailored to your audience with clean humor and sharp improvisation.",
         "A full-length stand‑up performance that blends quick observational humor, light audience interaction, "
         "and event‑specific jokes we prepare in advance based on a short brief you provide. The set scales from "
         "25 to 45 minutes, includes a professional sound check, and can be adapted for corporate events, "
         "birthdays, or community gatherings. We arrive early, coordinate with the MC/DJ, and ensure the flow "
         "between segments stays tight and engaging. Family‑friendly upon request.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Stand-upComedyNight.jpg",
         14, None, 20, 300, 0, "High", 1, 1,
         "Center", 120, 150.00, 4.00,
         "LaughLine", "+972-52-7000101", "book@laughline.co.il",
         2800.00, 20.00, 7, "Free cancellation up to 5 days before event.", 1),

        ("Close-up Magic Walkaround", "Entertainment", "Magician",
         "Sleight‑of‑hand magic that moves between tables and mingling guests.",
         "A roaming magician performs intimate illusions right at the guests’ hands: cards, coins, mentalism, "
         "and visual surprises. Perfect ice‑breaker during reception or between courses. No stage required; "
         "minimal setup and zero technical dependencies. Can operate in Hebrew or English and adapts to kids "
         "or adult audiences. Highly modular: book 60–120 minutes of continuous walkaround sets.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Close-upMagicWalkaround.jpg",
         6, None, 15, 250, 0, "Medium", 0, 0,
         "Jerusalem", 80, 120.00, 3.00,
         "Mirage Magic", "+972-53-7000102", "hello@miragemagic.co.il",
         1800.00, 10.00, 5, "Free cancellation up to 7 days before event.", 1),

        ("Fire & Light Juggling Show", "Show", "Juggling",
         "High‑energy fire and LED juggling set for outdoor evenings and large patios.",
         "A choreographed spectacle combining LED clubs, poi, and safe fire elements (when venue permits). "
         "The show is set to dynamic music and includes a short interactive segment with volunteers. "
         "We bring all safety equipment and a trained assistant. For venues that prohibit flame, we "
         "offer a pure LED edition with synchronized patterns and programmable visuals.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Fire&LightJugglingShow.jpg",
         8, None, 20, 400, 1, "High", 0, 0,
         "South", 200, 220.00, 5.00,
         "Orbit Arts", "+972-54-7000103", "team@orbitarts.co.il",
         3500.00, 18.00, 10, "Free cancellation up to 10 days before event.", 1),

        ("Live Caricature Station", "Entertainment", "Caricature",
         "On‑the‑spot caricatures that guests can take home as a keepsake.",
         "A professional caricaturist sets up a friendly mini‑studio and draws fast, flattering portraits. "
         "Average pace is 12–15 drawings per hour. We provide protective sleeves so guests can carry the art "
         "safely. Optionally brand the sheets with your logo or celebration date. Great for receptions, "
         "corporate family days, bar/bat‑mitzvahs and school fairs.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/LiveCaricatureStation.jpg",
         5, None, 10, 250, 0, "Low", 0, 0,
         "Sharon", 90, 90.00, 2.50,
         "Sketch&Smile", "+972-58-7000104", "draw@sketchnsmile.co.il",
         1200.00, 8.00, 3, "Free cancellation up to 3 days before event.", 1),

        ("Silent Disco – Multi Channel", "Entertainment", "SilentDisco",
         "Headphone‑based dance floor with two or three live music channels.",
         "We transform any hall or garden into a vibrant, neighbor‑friendly dance floor. Each guest receives "
         "wireless headphones and can switch channels between live DJ sets or curated playlists. "
         "Great for mixed audiences and venues with noise restrictions. We handle full deployment, "
         "charging logistics, sanitization, and on‑site technical support throughout the party.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/SilentDisco%E2%80%93MultiChannel.jpg",
         10, None, 30, 500, 1, "Medium", 0, 1,
         "Haifa", 140, 180.00, 3.50,
         "WaveHead", "+972-52-7000105", "book@wavehead.co.il",
         2600.00, 16.00, 7, "Free cancellation up to 7 days before event.", 1),

        ("Interactive Quiz Show", "Games", "Trivia",
         "Buzzers, big‑screen questions, and fast‑paced rounds with prizes.",
         "An emcee‑led quiz that combines pop culture, general knowledge, and "
         "event‑custom rounds (company history, family trivia). We provide wireless buzzers, projector, "
         "and score tracking. The format keeps all ages engaged through short, lively segments and finale "
         "rounds for the highest‑scoring teams.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/InteractiveQuizShow.jpg",
         8, None, 20, 200, 0, "Medium", 1, 1,
         "Center", 120, 140.00, 3.00,
         "BrightBuzz", "+972-53-7000106", "host@brightbuzz.co.il",
         2200.00, 12.00, 6, "Free cancellation up to 5 days before event.", 1),

        ("Escape Boxes – Mobile Puzzles", "Games", "EscapeGame",
         "Portable escape‑room experience for teams and classrooms.",
         "We bring a set of themed lock‑boxes, ciphers, and tactile puzzles that fit on tables and can be run "
         "anywhere without room builds. Facilitators guide the game, escalating hints on a timed track. "
         "Perfect for team‑building offsites, youth groups, and school activities. Difficulty is adjustable "
         "and can support multiple groups in parallel.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/EscapeBoxes%E2%80%93Mobile%20Puzzles.jpg",
         9, None, 12, 120, 0, "Medium", 0, 0,
         "Galilee", 160, 110.00, 2.50,
         "CipherCraft", "+972-57-7000107", "team@ciphercraft.co.il",
         1800.00, 14.00, 5, "Free cancellation up to 5 days before event.", 1),

        ("Retro Arcade Corner", "Games", "Arcade",
         "Plug‑and‑play arcade stations with classic titles and head‑to‑head play.",
         "Two to four multi‑game cabinets with authentic controls, great for all ages. "
         "We supply screens, stands, and cable management for a clean look. "
         "Attracts constant foot traffic during receptions and fairs. Requires a nearby power outlet.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/RetroArcadeCorner.jpg",
         6, None, 10, 150, 0, "Medium", 0, 1,
         "North", 180, 130.00, 3.00,
         "8Bit Events", "+972-58-7000108", "play@8bitevents.co.il",
         1600.00, 10.00, 4, "Free cancellation up to 7 days before event.", 1),

        ("Circus Mini‑Workshop & Show", "Kids", "Circus",
         "Playful circus skills intro plus a short show for kids and families.",
         "After a 10‑minute demo show, kids rotate through stations (spinning plates, juggling scarves, "
         "flower sticks, balance line) supervised by two facilitators. Safe gear and soft surfaces are provided. "
         "Wrap‑up showcase lets participants present a newly learned trick to applause.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/CircusMini%E2%80%91Workshop&Show.jpg",
         5, 12, 15, 120, 1, "Medium", 0, 0,
         "South", 150, 90.00, 2.00,
         "TinyCircus", "+972-55-7000109", "fun@tinycircus.co.il",
         1500.00, 8.00, 4, "Free cancellation up to 3 days before event.", 1),

        ("Bubble Art Show", "Kids", "Bubbles",
         "Stage bubbles, giant bubbles, and interactive bubble workshop.",
         "An enchanting performance that uses specialty bubble wands and safe, professional solution "
         "to create huge bubbles, bubble tunnels, and reflective shapes. Includes a photo moment inside "
         "a giant bubble for the birthday star or guest of honor. Works best indoors without heavy airflow.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/BubbleArtShow.jpg",
         3, 11, 15, 200, 0, "Low", 1, 0,
         "Center", 100, 80.00, 2.00,
         "BubbleJoy", "+972-52-7000110", "hello@bubblejoy.co.il",
         1400.00, 7.00, 3, "Free cancellation up to 3 days before event.", 1),

        # --- Workshops ---
        ("Chocolate Truffle Workshop", "Workshop", "Chocolate",
         "Hands‑on chocolate workshop with tempering basics and edible gifts.",
         "Participants learn to temper chocolate on marble, roll ganache truffles, and decorate with "
         "toppings. Every guest takes home a personal box. The session includes all ingredients, "
         "work surfaces, aprons, and food‑grade gloves. Adapts well to families and corporate groups.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/ChocolateTruffleWorkshop.jpg",
         7, None, 8, 60, 0, "Low", 0, 0,
         "Jerusalem", 70, 70.00, 1.80,
         "CacaoLab", "+972-53-7000111", "orders@cacaolab.co.il",
         1200.00, 35.00, 5, "Free cancellation up to 5 days before event.", 1),

        ("Watercolor & Lettering", "Workshop", "Art",
         "Relaxed art session covering watercolor washes and modern lettering.",
         "A guided creative break: build palettes, practice brush control, and compose a framed quote "
         "to take home. We bring all materials, cover tables, and set up drying racks. "
         "Suitable for beginners—no prior experience required.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Watercolor&Lettering.jpg",
         10, None, 8, 50, 0, "Low", 0, 0,
         "Sharon", 60, 60.00, 1.50,
         "Ink&Flow", "+972-58-7000112", "studio@inkflow.co.il",
         900.00, 32.00, 4, "Free cancellation up to 4 days before event.", 1),

        ("Sushi Rolling Class", "Workshop", "Culinary",
         "Intro to maki, uramaki, and simple nigiri with fresh ingredients.",
         "A practical culinary session that covers rice prep, knife safety, and rolling techniques. "
         "Guests rotate stations and plate their own tasting set. Vegetarian options available on request. "
         "Venue must allow food handling; we bring portable coolers.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/SushiRollingClass.jpg",
         12, None, 10, 40, 0, "Low", 0, 1,
         "Center", 80, 80.00, 2.00,
         "Roll&Joy", "+972-52-7000113", "chef@rollandjoy.co.il",
         1500.00, 45.00, 6, "Free cancellation up to 6 days before event.", 1),

        ("DIY Terrarium Workshop", "Workshop", "Plants",
         "Build a living terrarium in a glass vessel, layer by layer.",
         "We guide participants through substrate layers, plant placement, and long‑term care tips. "
         "Each attendee completes a personal terrarium to take home. Great for calm, mindful team sessions "
         "or boutique events.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/DIYTerrariumWorkshop.jpg",
         9, None, 8, 50, 0, "Low", 0, 0,
         "Haifa", 90, 65.00, 1.50,
         "GreenDome", "+972-54-7000114", "hello@greendome.co.il",
         1100.00, 38.00, 5, "Free cancellation up to 5 days before event.", 1),

        ("Drum Circle Energizer", "Workshop", "Rhythm",
         "Group drumming session that boosts energy and synchrony.",
         "Dozens of djembe and percussion instruments transform the group into an instant band. "
         "Our facilitators lead dynamic rhythms, call‑and‑response, and a celebratory finale. "
         "Ideal as an offsite opener or family‑day anchor activity.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/DrumCircleEnergizer.jpg",
         8, None, 15, 300, 1, "High", 0, 0,
         "North", 160, 120.00, 2.50,
         "PulseBeat", "+972-55-7000115", "beat@pulsebeat.co.il",
         2400.00, 18.00, 7, "Free cancellation up to 7 days before event.", 1),

        # --- Music ---
        ("DJ – Open Format Party", "Music", "DJ",
         "Versatile DJ set across decades and genres with seamless transitions.",
         "Pre‑event consultation to map your taste and timeline, live reading of the crowd, "
         "and professional MCing for key moments. Includes pro controller, basic lighting, and backup gear. "
         "Add‑ons: ceremony audio, dance‑floor lighting, or silent disco integration.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/DJ%E2%80%93OpenFormatParty.jpg",
         14, None, 40, 800, 0, "High", 0, 1,
         "Center", 180, 200.00, 3.50,
         "MixCraft", "+972-53-7000116", "mix@mixcraft.co.il",
         3200.00, 22.00, 8, "Free cancellation up to 10 days before event.", 1),

        ("Acoustic Duo (Guitar & Violin)", "Music", "LiveDuo",
         "Live acoustic duo for receptions and intimate sets.",
         "Elegant mix of classical themes, pop ballads, and Israeli favorites arranged for guitar and violin. "
         "We handle tasteful background amplification so conversation remains comfortable. "
         "Can perform indoors or on shaded patios.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/AcousticDuo(Guitar&Violin).jpg",
         10, None, 20, 300, 1, "Low", 0, 1,
         "Jerusalem", 100, 120.00, 2.00,
         "String&Pick", "+972-58-7000117", "duo@stringpick.co.il",
         2100.00, 18.00, 6, "Free cancellation up to 7 days before event.", 1),

        ("Klezmer Trio", "Music", "Klezmer",
         "Traditional and modern klezmer repertoire for simchas and festivals.",
         "Clarinet, accordion, and percussion create a joyful, uplifting sound. "
         "We can roam through the crowd or play on a small platform. "
         "Sets are modular and can bookend ceremonies or accompany dance segments.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/KlezmerTrio.jpg",
         8, None, 15, 300, 1, "Medium", 0, 0,
         "North", 140, 110.00, 2.00,
         "NigunBand", "+972-55-7000118", "book@nigunband.co.il",
         2400.00, 20.00, 5, "Free cancellation up to 7 days before event.", 1),

        # --- Speaker ---
        ("Motivational Keynote – Resilience at Work", "Speaker", "Motivation",
         "Insightful, story‑driven keynote on resilience and team alignment.",
         "A seasoned speaker shares field‑tested tools for navigating uncertainty, building habits, "
         "and keeping teams connected to purpose. The talk blends case studies, humor, and a short "
         "Q&A segment. Slides and handouts provided on request.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/MotivationalKeynote%E2%80%93ResilienceatWork.jpg",
         16, None, 20, 600, 0, "Medium", 1, 1,
         "Center", 220, 180.00, 3.00,
         "NorthStar Talks", "+972-52-7000119", "talks@northstar.co.il",
         4500.00, 0.00, 14, "Free cancellation up to 14 days before event.", 1),

        ("Tech Talk – AI for Non‑Engineers", "Speaker", "Tech",
         "Accessible introduction to practical AI tools for everyday workflows.",
         "Demonstrates real‑world use cases (summaries, drafting, analysis) without heavy jargon. "
         "Interactive segment invites participants to challenge a live demo. Tailored examples for "
         "marketing, HR, operations, and education audiences are available.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/TechTalk%E2%80%93AIforNon%E2%80%91Engineers.jpg",
         15, None, 20, 500, 0, "Low", 1, 1,
         "Haifa", 200, 160.00, 2.80,
         "BrightBridge", "+972-54-7000120", "ai@brightbridge.co.il",
         3800.00, 0.00, 10, "Free cancellation up to 10 days before event.", 1),

        # --- Kids (additional) ---
        ("Science Show – Spark Lab", "Kids", "Science",
         "Safe, spectacular science demos with audience participation.",
         "We present colorful reactions, air pressure tricks, and optical illusions that spark curiosity. "
         "All materials are classroom‑safe and leave no residue on venue floors. "
         "Optional add‑on: take‑home mini experiment kits.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/ScienceShow%E2%80%93SparkLab.jpg",
         6, 12, 20, 200, 0, "Medium", 1, 1,
         "Center", 120, 90.00, 2.00,
         "SparkLab", "+972-52-7000121", "lab@sparklab.co.il",
         1700.00, 12.00, 4, "Free cancellation up to 3 days before event.", 1),

        ("Puppet Theater Mini‑Musical", "Kids", "Puppets",
         "Charming puppet show with songs and life‑size characters.",
         "A portable stage, rich backdrops, and original music create a cozy theater experience. "
         "We include a short meet‑the‑puppets at the end for photos and smiles. "
         "Perfect for preschools, libraries, and community centers.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/PuppetTheaterMini%E2%80%91Musical.jpg",
         3, 9, 15, 150, 0, "Low", 1, 1,
         "Jerusalem", 90, 70.00, 1.50,
         "LittleCurtain", "+972-58-7000122", "show@littlecurtain.co.il",
         1300.00, 8.00, 3, "Free cancellation up to 3 days before event.", 1),

        ("Inflatable Play Park", "Kids", "Inflatables",
         "Colorful inflatables and games for schoolyards and community fields.",
         "We assemble a mini‑park of age‑appropriate inflatables, soft obstacles, and relay games. "
         "Our trained crew supervises rotations and ensures safe queueing. Requires outdoor space and "
         "nearby electricity for blowers.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/InflatablePlayPark.jpg",
         4, 13, 30, 500, 1, "High", 0, 1,
         "South", 220, 220.00, 4.00,
         "JumpZone", "+972-53-7000123", "park@jumpzone.co.il",
         3200.00, 10.00, 7, "Free cancellation up to 7 days before event.", 1),

        # --- More Games ---
        ("Giant Board Games Lawn", "Games", "YardGames",
         "Oversized checkers, Jenga, Connect‑Four, and ring toss for lawns and patios.",
         "Casual, free‑play zone that encourages mingling between generations. "
         "We supply mats, shade posts (if needed), and signage for quick rules. "
         "Works well as a background attraction throughout the event.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/GiantBoardGamesLawn.jpg",
         5, None, 15, 300, 1, "Low", 0, 0,
         "Sharon", 120, 110.00, 2.00,
         "PlayYard", "+972-57-7000124", "hello@playyard.co.il",
         1500.00, 7.00, 4, "Free cancellation up to 4 days before event.", 1),

        ("Laser Tag Arena – Mobile", "Games", "LaserTag",
         "Pop‑up laser tag with inflatable bunkers and sensors.",
         "We deploy a modular field with bunkers, team bases, and safe infrared taggers. "
         "Great for youth groups and company fun days. Operates day or night with LED identifiers. "
         "Requires open area (indoor gym or outdoor field).",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/LaserTagArena%E2%80%93Mobile.jpg",
         9, None, 12, 200, 1, "High", 0, 0,
         "Galilee", 200, 160.00, 3.00,
         "PhotonPlay", "+972-55-7000125", "ops@photonplay.co.il",
         2600.00, 14.00, 6, "Free cancellation up to 6 days before event.", 1),

        ("Mobile Archery Range", "Games", "Archery",
         "Foam‑tip archery with safety nets and instructor guidance.",
         "Guests learn stance, draw, and aim with low‑poundage bows. We erect safety netting and lane markers "
         "and operate in controlled rounds. Weather permitting, can be hosted on lawns or large halls.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/MobileArcheryRange.jpg",
         10, None, 10, 150, 1, "Medium", 0, 0,
         "North", 160, 140.00, 2.50,
         "AimTrue", "+972-58-7000126", "coach@aimtrue.co.il",
         1800.00, 12.00, 5, "Free cancellation up to 5 days before event.", 1),

        # --- Additional Entertainment ---
        ("Photo Booth – DSLR Studio", "Entertainment", "PhotoBooth",
         "Professional DSLR photo booth with instant prints and digital gallery.",
         "We bring studio‑grade lighting, themed props, and custom overlays. "
         "Guests receive high‑quality prints on the spot and a link to the full gallery afterward. "
         "Fits into small corners and keeps lines moving quickly with an attendant.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/PhotoBooth%E2%80%93DSLRStudio.jpg",
         8, None, 20, 400, 0, "Medium", 0, 1,
         "Center", 120, 150.00, 3.00,
         "SnapBox", "+972-52-7000127", "studio@snapbox.co.il",
         2400.00, 10.00, 6, "Free cancellation up to 6 days before event.", 1),

        ("Henna Tradition Experience", "Entertainment", "Henna",
         "Cultural henna celebration with attire, music, and guided ceremony.",
         "We create an authentic atmosphere with décor, traditional garments for the family, and rhythmic music. "
         "The lead hostess explains each step and invites guests to participate respectfully. "
         "All cosmetics are skin‑safe and removable.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/HennaTraditionExperience.jpg",
         12, None, 30, 400, 0, "Medium", 1, 1,
         "South", 200, 180.00, 3.50,
         "Heritage Events", "+972-54-7000128", "hello@heritageevents.co.il",
         3600.00, 14.00, 10, "Free cancellation up to 10 days before event.", 1),

        ("Stilt Walkers Parade", "Entertainment", "Parade",
         "Colorful stilt walkers that greet and entertain during entrances.",
         "Two to three performers in impressive costumes roam and pose for photos, creating a festive "
         "arrival experience. Ideal for plazas, promenades, and wide hallways. No stage needed.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/StiltWalkersParade.jpg",
         6, None, 20, 600, 1, "High", 0, 0,
         "Haifa", 160, 140.00, 2.80,
         "SkyHigh Crew", "+972-55-7000129", "book@skyhighcrew.co.il",
         2300.00, 9.00, 5, "Free cancellation up to 7 days before event.", 1),

        ("Balloon Twisting Artist", "Entertainment", "BalloonArtist",
         "Creative balloon sculptures customized to guest requests.",
         "Fast, friendly balloon art that delights kids and adults alike—flowers, swords, hats, animals, "
         "and themed creations. Great roaming add‑on for receptions or queue areas.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/BalloonTwistingArtist.jpg",
         3, None, 10, 250, 0, "Low", 0, 0,
         "Jerusalem", 80, 70.00, 1.50,
         "Twist&Joy", "+972-53-7000130", "twist@joy.co.il",
         900.00, 6.00, 3, "Free cancellation up to 2 days before event.", 1),

        ("Face Painting Corner", "Entertainment", "FacePaint",
         "Face painting with skin‑safe colors and glitter accents.",
         "We bring illustrated design menus for fast choice and use professional, dermatologically tested "
         "paints. Efficient queue management keeps kids happy and lines short. "
         "Includes cleaning wipes and after‑care tips for parents.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/FacePaintingCorner.jpg",
         3, 11, 10, 220, 0, "Low", 0, 0,
         "Sharon", 90, 70.00, 1.40,
         "ColorPop", "+972-58-7000131", "paint@colorpop.co.il",
         950.00, 6.00, 3, "Free cancellation up to 2 days before event.", 1),

        # --- More Music ---
        ("Singer‑Guitarist Solo", "Music", "Soloist",
         "Warm vocal set with acoustic guitar across pop, folk, and Israeli classics.",
         "Perfect for receptions and intimate dinners. We bring compact amplification and "
         "a tasteful repertoire that can include your requests with advance notice.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Singer%E2%80%91GuitaristSolo.jpg",
         12, None, 20, 250, 0, "Low", 0, 1,
         "Center", 100, 100.00, 2.00,
         "SongLeaf", "+972-52-7000132", "sing@songleaf.co.il",
         1600.00, 14.00, 5, "Free cancellation up to 5 days before event.", 1),

        ("String Quartet", "Music", "Quartet",
         "Classical string quartet for ceremonies and upscale receptions.",
         "Two violins, viola, and cello performing elegant arrangements—from Bach to movie themes. "
         "Ideal for aisles, chuppahs, and cocktail hours. Professional black‑tie presentation.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/StringQuartet.jpg",
         14, None, 20, 400, 0, "Low", 0, 1,
         "Jerusalem", 120, 160.00, 3.00,
         "Arioso Ensemble", "+972-58-7000133", "hello@arioso.co.il",
         3600.00, 24.00, 10, "Free cancellation up to 10 days before event.", 1),

        ("Percussion After‑Party Crew", "Music", "Percussion",
         "Live percussion overlay that supercharges the dance floor.",
         "Two percussionists join the DJ with congas, bongos, and shakers, building live rhythms "
         "that ride the beat and lift energy. Works brilliantly for Latin and Mediterranean sets.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/PercussionAfter%E2%80%91PartyCrew.jpg",
         14, None, 40, 800, 0, "High", 0, 0,
         "South", 200, 150.00, 3.20,
         "GrooveFuel", "+972-54-7000134", "groove@groovefuel.co.il",
         2200.00, 16.00, 7, "Free cancellation up to 7 days before event.", 1),

        # --- Additional Workshops ---
        ("Barista Skills Crash Course", "Workshop", "Coffee",
         "Hands‑on espresso and milk‑art session led by a pro barista.",
         "We cover grinder calibration, espresso extraction, milk steaming, and simple latte‑art patterns. "
         "Mobile coffee stations keep groups rotating smoothly. Caffeine‑happy smiles guaranteed.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/BaristaSkillsCrashCourse.jpg",
         14, None, 8, 40, 0, "Low", 0, 1,
         "Center", 100, 90.00, 2.20,
         "CremaLab", "+972-53-7000135", "coffee@cremalab.co.il",
         1300.00, 34.00, 5, "Free cancellation up to 5 days before event.", 1),

        ("Candle Making & Scent Blending", "Workshop", "Craft",
         "Craft soy‑wax candles with personalized scents and labels.",
         "Participants choose fragrance families, wick sizes, and vessel styles, "
         "then pour and label their own candle. We bring all supplies and protective covers.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/CandleMaking&ScentBlending.jpg",
         9, None, 8, 50, 0, "Low", 0, 0,
         "Haifa", 80, 70.00, 1.60,
         "AromaCraft", "+972-58-7000136", "craft@aromacraft.co.il",
         1100.00, 30.00, 4, "Free cancellation up to 4 days before event.", 1),

        ("Graffiti & Street‑Art Tour", "Workshop", "UrbanArt",
         "Guided graffiti walk with hands‑on stencil station at the end.",
         "Explore local street‑art stories, techniques, and artist signatures in a lively urban route. "
         "Wrap up with a supervised stencil activity on takeaway boards. "
         "Great photo opportunities throughout.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Graffiti&Street%E2%80%91ArtTour.jpg",
         12, None, 10, 60, 1, "Medium", 0, 0,
         "Center", 60, 60.00, 1.50,
         "UrbanCanvas", "+972-52-7000137", "tour@urbancanvas.co.il",
         1000.00, 22.00, 3, "Free cancellation up to 3 days before event.", 1),

        # --- Speaker (additional) ---
        ("Financial Wellness 101", "Speaker", "Finance",
         "Clear, friendly session on budgeting, saving, and long‑term planning.",
         "A pragmatic talk that demystifies personal finance basics with realistic examples and "
         "actionable checklists. Optional Q&A and worksheet downloads afterward.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/FinancialWellness101.jpg",
         16, None, 20, 400, 0, "Low", 1, 0,
         "Sharon", 120, 110.00, 2.50,
         "BrightLedger", "+972-53-7000138", "money@brightledger.co.il",
         2800.00, 0.00, 8, "Free cancellation up to 8 days before event.", 1),

        # --- More Kids ---
        ("Lego Engineering Lab", "Kids", "Lego",
         "STEM‑based Lego challenges with ramps, gears, and mini‑motors.",
         "Kids collaborate in teams to build and iterate on fun engineering tasks. "
         "Facilitators coach problem‑solving and creativity, ending with short demos.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/LegoEngineeringLab.jpg",
         6, 12, 12, 120, 0, "Low", 0, 0,
         "Center", 80, 70.00, 1.50,
         "BrickWorks", "+972-58-7000139", "lab@brickworks.co.il",
         1300.00, 10.00, 4, "Free cancellation up to 4 days before event.", 1),

        ("Storytelling & Illustration Hour", "Kids", "StoryTime",
         "Cozy story time with live illustration on a big pad.",
         "Interactive reading with funny voices, creative prompts, and quick drawings that bring characters to life. "
         "Kids vote on twists and endings to co‑create the tale.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Storytelling&IllustrationHour.jpg",
         3, 9, 10, 100, 0, "Low", 0, 0,
         "Jerusalem", 60, 60.00, 1.20,
         "PaperMoon", "+972-53-7000140", "read@papermoon.co.il",
         800.00, 6.00, 3, "Free cancellation up to 2 days before event.", 1),

        # --- Extras to reach 40 ---
        ("Mind Reading Stage Act", "Show", "Mentalist",
         "Psychological illusions and audience mind‑reading segments.",
         "A polished mentalism show featuring predictions, drawing duplications, and thought reveals. "
         "Requires a quiet audience and stage lighting for best impact. Can integrate the guest of honor "
         "in a respectful, memorable centerpiece routine.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/MindReadingStageAct.jpg",
         12, None, 30, 600, 1, "Medium", 1, 1,
         "Center", 180, 180.00, 3.20,
         "MindScope", "+972-52-7000141", "show@mindscope.co.il",
         4200.00, 0.00, 12, "Free cancellation up to 12 days before event.", 1),

        ("LED Dance Troupe", "Show", "Dance",
         "High‑impact LED dance with programmable costumes and visuals.",
         "A troupe of four dancers performs synchronized choreography using custom LED suits that paint "
         "patterns in the air. Ideal for grand reveals and product launches. Fits most stages or open plazas.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/LEDDanceTroupe.jpg",
         8, None, 40, 1000, 1, "High", 1, 1,
         "Haifa", 220, 220.00, 4.00,
         "NeonMotion", "+972-55-7000142", "dance@neonmotion.co.il",
         5200.00, 0.00, 14, "Free cancellation up to 14 days before event.", 1),

        ("Vintage Jazz Trio", "Music", "Jazz",
         "Swing and bossa‑nova classics with a classy lounge vibe.",
         "Upright bass, guitar, and vocals deliver smooth standards and tasteful instrumentals. "
         "Volume is carefully controlled to allow easy conversation during dinners or cocktails.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/VintageJazzTrio.jpg",
         14, None, 20, 300, 0, "Low", 0, 1,
         "Sharon", 140, 130.00, 2.50,
         "VelvetRoom", "+972-53-7000143", "jazz@velvetroom.co.il",
         2600.00, 20.00, 8, "Free cancellation up to 8 days before event.", 1),

        ("Mediterranean Dabke Workshop", "Workshop", "Dance",
         "Folkloric dabke steps taught in a joyful circle format.",
         "A dance leader breaks down steps and patterns so all ages can join. "
         "We start slow and end with a lively chain through the crowd—great for weddings and community nights.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/MediterraneanDabkeWorkshop.jpg",
         8, None, 20, 300, 1, "Medium", 0, 0,
         "North", 160, 120.00, 2.50,
         "StepTogether", "+972-58-7000144", "dance@steptogether.co.il",
         1700.00, 12.00, 6, "Free cancellation up to 6 days before event.", 1),

        ("Outdoor Cinema Night", "Entertainment", "Cinema",
         "Large‑screen outdoor cinema with projector, screen, and FM audio option.",
         "We build a cozy outdoor theater with blankets and low chairs on request. "
         "Includes licensing guidance for public screenings and weather contingency tips.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/OutdoorCinemaNight.jpg",
         8, None, 20, 500, 1, "Medium", 0, 1,
         "South", 220, 180.00, 3.50,
         "SkyFrame", "+972-54-7000145", "cinema@skyframe.co.il",
         2900.00, 12.00, 7, "Free cancellation up to 7 days before event.", 1),

        ("Improv Theater Games", "Workshop", "Improv",
         "Fast, funny improv exercises that unlock creativity and team trust.",
         "We facilitate high‑energy rounds that emphasize listening, acceptance, and playful risk‑taking. "
         "No acting experience needed—just willingness to laugh and participate.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/ImprovTheaterGames.jpg",
         14, None, 12, 150, 0, "Medium", 1, 1,
         "Center", 100, 100.00, 2.00,
         "YesAnd Studio", "+972-58-7000147", "play@yesand.co.il",
         1700.00, 14.00, 5, "Free cancellation up to 5 days before event.", 1),

        ("Storyteller – Folktales Evening", "Speaker", "Storytelling",
         "Captivating folktales with live musical interludes.",
         "A professional storyteller weaves humorous and heartfelt tales drawn from local and global traditions. "
         "Ideal for community nights and intimate cultural events. Small amplification provided if needed.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Storyteller%E2%80%93FolktalesEvening.jpg",
         12, None, 20, 300, 0, "Low", 1, 1,
         "Jerusalem", 100, 90.00, 2.00,
         "Tale&Tune", "+972-53-7000148", "tales@taletune.co.il",
         1600.00, 10.00, 6, "Free cancellation up to 6 days before event.", 1),

        ("UV Face‑Paint Glow Party", "Entertainment", "GlowParty",
         "Neon glow body‑safe paints with blacklights and DJ playlist integration.",
         "We set up UV lighting zones and provide quick, festival‑style designs for guests. "
         "Creates striking photos and an instant party vibe. Works best in darker spaces.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/UVFace%E2%80%91PaintGlowParty.jpg",
         10, None, 20, 500, 0, "High", 0, 1,
         "Haifa", 180, 150.00, 3.00,
         "GlowBox", "+972-55-7000149", "uv@glowbox.co.il",
         2100.00, 12.00, 6, "Free cancellation up to 6 days before event.", 1),

       ("Social Photo Challenge", "Games", "Scavenger",
         "Mobile scavenger hunt with creative photo missions and leaderboard.",
         "Teams complete location‑based prompts and upload photos to a live feed. "
         "Facilitators moderate challenges and count bonus points for creativity and teamwork.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/SocialPhotoChallenge.jpg",
         12, None, 12, 400, 1, "Medium", 0, 1,
         "Center", 180, 140.00, 2.80,
         "SnapQuest", "+972-55-7000152", "ops@snapquest.co.il",
         1900.00, 10.00, 6, "Free cancellation up to 6 days before event.", 1),

        ("Meditation & Breathwork", "Workshop", "Mindfulness",
         "Guided relaxation and breath techniques for calm focus.",
         "A quiet, science‑informed session that introduces breathing patterns and micro‑breaks "
         "for daily resilience. Can be hosted in offices, schools, or outdoor gardens.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Meditation&Breathwork.jpg",
         12, None, 8, 120, 0, "Low", 0, 0,
         "Sharon", 100, 80.00, 1.50,
         "StillPoint", "+972-53-7000153", "calm@stillpoint.co.il",
         900.00, 14.00, 3, "Free cancellation up to 3 days before event.", 1),

        ("Story Slam – Open Mic", "Entertainment", "OpenMic",
         "Hosted storytelling night where guests share 5‑minute true tales.",
         "We provide a friendly host, stage timer, and light coaching to keep the stories crisp and "
         "uplifting. Optional judges and small prizes for a playful competitive twist.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/StorySlam%E2%80%93OpenMic.jpg",
         16, None, 30, 300, 0, "Medium", 1, 1,
         "Jerusalem", 120, 110.00, 2.20,
         "Mic&Light", "+972-58-7000154", "host@miclight.co.il",
         1700.00, 10.00, 7, "Free cancellation up to 7 days before event.", 1),

        ("Outdoor Team Olympics", "Games", "FieldGames",
         "Lighthearted field competitions with relays, puzzles, and teamwork challenges.",
         "We set up stations around your venue—sack races, human knots, logic towers—and rotate teams "
         "through timed heats. Emphasis on collaboration and fun over athletic ability.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/OutdoorTeamOlympics.jpg",
         10, None, 20, 400, 1, "Medium", 0, 0,
         "South", 240, 220.00, 4.00,
         "PlayWorks", "+972-55-7000155", "field@playworks.co.il",
         2600.00, 12.00, 6, "Free cancellation up to 6 days before event.", 1),

        ("Poetry & Music Duo", "Speaker", "Poetry",
         "Spoken‑word poetry accompanied by live guitar for atmospheric evenings.",
         "Original texts and classic pieces performed in a warm, intimate style. "
         "Can anchor a cultural night or serve as an interlude between program segments.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Poetry&MusicDuo.jpg",
         14, None, 20, 250, 0, "Low", 1, 1,
         "Galilee", 120, 90.00, 1.80,
         "Lines&Chords", "+972-58-7000157", "poetry@lineschords.co.il",
         1500.00, 8.00, 5, "Free cancellation up to 5 days before event.", 1),

        ("Glow Stick Night Run (Fun‑Run)", "Games", "NightRun",
         "Short, festive night run with glow sticks and upbeat playlist.",
         "We mark a 1–3 km loop with safe lighting and marshals, run warm‑up, and cheer stations. "
         "Family‑friendly pace; medals and photos at the finish line.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/GlowStickNightRun(Fun%E2%80%91Run).jpg",
         8, None, 30, 800, 1, "High", 0, 1,
         "Center", 260, 240.00, 4.50,
         "BrightRun", "+972-53-7000158", "run@brightrun.co.il",
         3000.00, 8.00, 7, "Free cancellation up to 7 days before event.", 1),

        ("Hands‑on Photography Basics", "Workshop", "Photography",
         "Practical camera workshop covering composition, light, and focus.",
         "Participants shoot mini‑assignments and get instant feedback. "
         "Great as a creative team activity or enrichment hour for teens.",
         "https://cdn.jsdelivr.net/gh/MaiEden/pic-DB-events-app@main/service/Hands%E2%80%91onPhotographyBasics.jpg",
         12, None, 8, 40, 0, "Low", 0, 1,
         "Haifa", 100, 80.00, 1.80,
         "FocusPoint", "+972-55-7000160", "photo@focuspoint.co.il",
         1000.00, 18.00, 4, "Free cancellation up to 4 days before event.", 1),
    ]

    # Insert
    db.execute_many(
        """
        INSERT INTO dbo.ServiceOption
            (ServiceName, Category, Subcategory, ShortDescription, Description, PhotoUrl,
             MinAge, MaxAge, MinParticipants, MaxParticipants,
             IsOutdoor, NoiseLevel, StageRequired, RequiresElectricity,
             Region, TravelLimitKm, TravelFeeBase, TravelFeePerKm,
             VendorName, ContactPhone, ContactEmail,
             BasePrice, PricePerPerson, LeadTimeDays, CancellationPolicy, Available)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        services
    )

    print(f"Service seeding completed successfully with {len(services)} records.")


if __name__ == "__main__":
    seed()
