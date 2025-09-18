"""
create_schema.py
Create DB schema for Events app.
"""
from server.gateway.DBgateway import DbGateway

SCHEMA_SQL = """
-- Users
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Users')
BEGIN
    CREATE TABLE dbo.Users (
        UserId INT IDENTITY(1,1) PRIMARY KEY,
        Phone NVARCHAR(30) NOT NULL,
        Username NVARCHAR(100) NOT NULL UNIQUE,
        PasswordHash NVARCHAR(200) NOT NULL,
        Region NVARCHAR(50) NOT NULL
    );
END;

-- === Services tables ===

-- Halls
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Hall')
BEGIN
    CREATE TABLE dbo.Hall (
        HallId INT IDENTITY(1,1) PRIMARY KEY,
        HallName NVARCHAR(200) NOT NULL,
        HallType NVARCHAR(100) NOT NULL,       -- Synagogue / Restaurant / Garden...
        Capacity INT NULL,
        Region NVARCHAR(50) NOT NULL,
        Latitude DECIMAL(9,6) NULL,
        Longitude DECIMAL(9,6) NULL,
        Description NVARCHAR(MAX) NULL,
        PricePerHour DECIMAL(10,2) NULL,
        PricePerDay DECIMAL(10,2) NULL,
        PricePerPerson DECIMAL(10,2) NULL,
        ParkingAvailable BIT NOT NULL DEFAULT 0,
        WheelchairAccessible BIT NOT NULL DEFAULT 0,
        ContactPhone NVARCHAR(50) NULL,
        ContactEmail NVARCHAR(200) NULL,
        WebsiteUrl NVARCHAR(500) NULL,
        PhotoUrl NVARCHAR(500) NULL
    );
END;

-- decoration options
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'DecorOption')
BEGIN
    CREATE TABLE dbo.DecorOption (
        DecorId INT IDENTITY(1,1) CONSTRAINT PK_DecorOption PRIMARY KEY,

        -- description and ID
        DecorName NVARCHAR(200) NOT NULL,
        Category  NVARCHAR(50)  NOT NULL,
        Theme     NVARCHAR(100) NULL,
        Description NVARCHAR(MAX) NULL,

        -- Matching and logistics
        Indoor BIT NOT NULL CONSTRAINT DF_DecorOption_Indoor DEFAULT (1),
        RequiresElectricity BIT NOT NULL CONSTRAINT DF_DecorOption_ReqElec DEFAULT (0),
        SetupDurationMinutes    INT NULL,
        TeardownDurationMinutes INT NULL,

        -- Pricing by place size
        PriceSmall  DECIMAL(10,2) NULL,
        PriceMedium DECIMAL(10,2) NULL,
        PriceLarge  DECIMAL(10,2) NULL,
        DeliveryFee DECIMAL(10,2) NULL,

        -- Geographical details and supplier
        Region       NVARCHAR(50)  NULL,
        VendorName   NVARCHAR(200) NULL,
        ContactPhone NVARCHAR(50)  NULL,
        ContactEmail NVARCHAR(200) NULL,

        -- photo
        PhotoUrl NVARCHAR(500) NULL,

        -- Availability and policies
        LeadTimeDays       INT NULL,
        CancellationPolicy NVARCHAR(500) NULL,
        Available BIT NOT NULL CONSTRAINT DF_DecorOption_Available DEFAULT (1),

        -- Constraints
        CONSTRAINT CK_DecorOption_Category CHECK (Category IN (
            N'Balloons',
            N'Flowers',
            N'Tableware',
            N'Linens',
            N'Lighting',
            N'Backdrop',
            N'CakeStands',
            N'Props',
            N'Centerpieces',
            N'Signage'
        )),
        CONSTRAINT CK_DecorOption_SetupNonNegative CHECK (
            (SetupDurationMinutes    IS NULL OR SetupDurationMinutes    >= 0) AND
            (TeardownDurationMinutes IS NULL OR TeardownDurationMinutes >= 0)
        ),
        CONSTRAINT CK_DecorOption_PricesNonNegative CHECK (
            (PriceSmall  IS NULL OR PriceSmall  >= 0) AND
            (PriceMedium IS NULL OR PriceMedium >= 0) AND
            (PriceLarge  IS NULL OR PriceLarge  >= 0) AND
            (DeliveryFee IS NULL OR DeliveryFee >= 0)
        ),
        CONSTRAINT CK_DecorOption_AtLeastOnePrice CHECK (
            ISNULL(PriceSmall,0) + ISNULL(PriceMedium,0) + ISNULL(PriceLarge,0) > 0
        ),
        CONSTRAINT CK_DecorOption_LeadTimeNonNegative CHECK (LeadTimeDays IS NULL OR LeadTimeDays >= 0),
        CONSTRAINT CK_DecorOption_EmailFormat CHECK (
            ContactEmail IS NULL OR ContactEmail LIKE N'%@%._%'
        )
    );

    -- Useful indexes
    CREATE INDEX IX_DecorOption_Category  ON dbo.DecorOption(Category);
    CREATE INDEX IX_DecorOption_Region    ON dbo.DecorOption(Region);
    CREATE INDEX IX_DecorOption_Vendor    ON dbo.DecorOption(VendorName);
    CREATE INDEX IX_DecorOption_Available ON dbo.DecorOption(Available) WHERE Available = 1;
END;

-- Services
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'ServiceOption')
BEGIN
    CREATE TABLE dbo.ServiceOption (
        -- description and ID
        ServiceId INT IDENTITY(1,1) CONSTRAINT PK_ServiceOption PRIMARY KEY,
        ServiceName NVARCHAR(200) NOT NULL,
        Category NVARCHAR(50) NOT NULL,
        Subcategory NVARCHAR(100) NULL,
        ShortDescription NVARCHAR(300) NULL,
        Description NVARCHAR(MAX) NULL,
        PhotoUrl NVARCHAR(500) NULL,

        -- Audience and place requirements
        MinAge INT NULL,
        MaxAge INT NULL,
        MinParticipants INT NULL,
        MaxParticipants INT NULL,

        IsOutdoor BIT NOT NULL CONSTRAINT DF_ServiceOption_IsOutdoor DEFAULT (0),  -- 0=Indoor, 1=Outdoor
        NoiseLevel NVARCHAR(10) NULL,                                              -- Low/Medium/High
        StageRequired BIT NOT NULL CONSTRAINT DF_ServiceOption_StageReq DEFAULT (0),
        RequiresElectricity BIT NOT NULL CONSTRAINT DF_ServiceOption_ReqElec DEFAULT (0),

        -- Location and provider
        Region NVARCHAR(50) NULL,
        TravelLimitKm INT NULL,
        TravelFeeBase DECIMAL(10,2) NULL,
        TravelFeePerKm DECIMAL(10,2) NULL,
        VendorName NVARCHAR(200) NULL,
        ContactPhone NVARCHAR(50) NULL,
        ContactEmail NVARCHAR(200) NULL,

        -- Pricing and availability
        BasePrice DECIMAL(10,2) NULL,         -- base price for event
        PricePerPerson DECIMAL(10,2) NULL,    -- price per person (optional)
        LeadTimeDays INT NULL,
        CancellationPolicy NVARCHAR(500) NULL,
        Available BIT NOT NULL CONSTRAINT DF_ServiceOption_Available DEFAULT (1),

        /* ---------------- Constraints ---------------- */

        -- Enums
        CONSTRAINT CK_ServiceOption_Category CHECK (Category IN (
            N'Entertainment', N'Workshop', N'Show', N'Kids', N'Music', N'Speaker', N'Games'
        )),
        CONSTRAINT CK_ServiceOption_Noise CHECK (NoiseLevel IS NULL OR NoiseLevel IN (N'Low', N'Medium', N'High')),

        -- Age/participants ranges
        CONSTRAINT CK_ServiceOption_AgeRange CHECK (
            (MinAge IS NULL OR MinAge >= 0) AND
            (MaxAge IS NULL OR MaxAge >= 0) AND
            (MinAge IS NULL OR MaxAge IS NULL OR MinAge <= MaxAge)
        ),
        CONSTRAINT CK_ServiceOption_ParticipantsRange CHECK (
            (MinParticipants IS NULL OR MinParticipants >= 0) AND
            (MaxParticipants IS NULL OR MaxParticipants >= 0) AND
            (MinParticipants IS NULL OR MaxParticipants IS NULL OR MinParticipants <= MaxParticipants)
        ),

        -- Non-negative of numbers/prices/distances/days
        CONSTRAINT CK_ServiceOption_NonNegative CHECK (
            (TravelLimitKm    IS NULL OR TravelLimitKm    >= 0) AND
            (TravelFeeBase    IS NULL OR TravelFeeBase    >= 0) AND
            (TravelFeePerKm   IS NULL OR TravelFeePerKm   >= 0) AND
            (BasePrice        IS NULL OR BasePrice        >= 0) AND
            (PricePerPerson   IS NULL OR PricePerPerson   >= 0) AND
            (LeadTimeDays     IS NULL OR LeadTimeDays     >= 0)
        ),

        -- At least one pricing model (basic or per person)
        CONSTRAINT CK_ServiceOption_AtLeastOnePrice CHECK (
            ISNULL(BasePrice,0) + ISNULL(PricePerPerson,0) > 0
        ),

        -- Basic email verification
        CONSTRAINT CK_ServiceOption_EmailFormat CHECK (
            ContactEmail IS NULL OR ContactEmail LIKE N'%@%._%'
        )
    );

    /* ---------------- indexes ---------------- */
    CREATE INDEX IX_Service_Category   ON dbo.ServiceOption(Category);
    CREATE INDEX IX_Service_Region     ON dbo.ServiceOption(Region);
    CREATE INDEX IX_Service_Available  ON dbo.ServiceOption(Available) WHERE Available = 1;
    CREATE INDEX IX_Service_Vendor     ON dbo.ServiceOption(VendorName);
    CREATE INDEX IX_Service_BasePrice  ON dbo.ServiceOption(BasePrice);
    CREATE INDEX IX_Service_PricePerPs ON dbo.ServiceOption(PricePerPerson);
END;

-- link tables 

-- User ↔ Decor
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='UserDecor' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.UserDecor (
        UserId INT NOT NULL,
        DecorId INT NOT NULL,
        RelationType NVARCHAR(10) NOT NULL,  -- 'OWNER' or 'USER'
        CONSTRAINT PK_UserDecor PRIMARY KEY (UserId, DecorId),
        CONSTRAINT CK_UserDecor_RelationType CHECK (RelationType IN ('OWNER','USER')),
        CONSTRAINT FK_UserDecor_User  FOREIGN KEY (UserId)  REFERENCES dbo.Users(UserId)       ON DELETE CASCADE,
        CONSTRAINT FK_UserDecor_Decor FOREIGN KEY (DecorId) REFERENCES dbo.DecorOption(DecorId) ON DELETE CASCADE
    );
    CREATE INDEX IX_UserDecor_Decor    ON dbo.UserDecor(DecorId);
    CREATE INDEX IX_UserDecor_Relation ON dbo.UserDecor(RelationType);
END;

-- User ↔ Hall
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='UserHall' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.UserHall (
        UserId INT NOT NULL,
        HallId INT NOT NULL,
        RelationType NVARCHAR(10) NOT NULL,  -- 'OWNER' or 'USER'
        CONSTRAINT PK_UserHall PRIMARY KEY (UserId, HallId),
        CONSTRAINT CK_UserHall_RelationType CHECK (RelationType IN ('OWNER','USER')),
        CONSTRAINT FK_UserHall_User FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId) ON DELETE CASCADE,
        CONSTRAINT FK_UserHall_Hall FOREIGN KEY (HallId) REFERENCES dbo.Hall(HallId) ON DELETE CASCADE
    );
    CREATE INDEX IX_UserHall_Hall      ON dbo.UserHall(HallId);
    CREATE INDEX IX_UserHall_Relation  ON dbo.UserHall(RelationType);
END;

-- User ↔ Service
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='UserServiceLink' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.UserServiceLink (
        UserId INT NOT NULL,
        ServiceId INT NOT NULL,
        RelationType NVARCHAR(10) NOT NULL,  -- 'OWNER' or 'USER'
        CONSTRAINT PK_UserServiceLink PRIMARY KEY (UserId, ServiceId),
        CONSTRAINT CK_UserServiceLink_RelationType CHECK (RelationType IN ('OWNER','USER')),
        CONSTRAINT FK_UserServiceLink_User    FOREIGN KEY (UserId)    REFERENCES dbo.Users(UserId)           ON DELETE CASCADE,
        CONSTRAINT FK_UserServiceLink_Service FOREIGN KEY (ServiceId) REFERENCES dbo.ServiceOption(ServiceId) ON DELETE CASCADE
    );
    CREATE INDEX IX_UserServiceLink_Service  ON dbo.UserServiceLink(ServiceId);
    CREATE INDEX IX_UserServiceLink_Relation ON dbo.UserServiceLink(RelationType);
END;
"""

def main() -> None:
    db = DbGateway()
    db.execute(SCHEMA_SQL, commit=True)
    print("Polymorphic schema created successfully.")

if __name__ == "__main__":
    main()