"""
create_schema_poly.py
Create polymorphic schema for Events app.
Each service has its own table, linked via (ServiceType, ServiceKey).
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

-- Events
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Event')
BEGIN
    CREATE TABLE dbo.Event (
        EventId INT IDENTITY(1,1) PRIMARY KEY,
        EventDate DATE NOT NULL,
        EventTime TIME(0) NOT NULL,
        EventType NVARCHAR(100) NOT NULL,
        ManagerUserId INT NOT NULL,
        CONSTRAINT FK_Event_User FOREIGN KEY (ManagerUserId)
            REFERENCES dbo.Users(UserId)
    );
END;

-- UserService mapping
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='UserService')
BEGIN
    CREATE TABLE dbo.UserService (
        UserId INT NOT NULL,
        ServiceType NVARCHAR(50) NOT NULL,  -- e.g. 'Hall', 'DJ'
        ServiceKey INT NOT NULL,            -- the PK in that service table
        PRIMARY KEY (UserId, ServiceType, ServiceKey),
        CONSTRAINT FK_UserService_User FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId) ON DELETE CASCADE
    );
END;

-- EventService mapping
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='EventService')
BEGIN
    CREATE TABLE dbo.EventService (
        EventId INT NOT NULL,
        ServiceType NVARCHAR(50) NOT NULL,
        ServiceKey INT NOT NULL,
        PRIMARY KEY (EventId, ServiceType, ServiceKey),
        CONSTRAINT FK_EventService_Event FOREIGN KEY (EventId) REFERENCES dbo.Event(EventId) ON DELETE CASCADE
    );
END;

-- === Service-specific tables ===

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

-- DJs
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='DJ')
BEGIN
    CREATE TABLE dbo.DJ (
        DJId INT IDENTITY(1,1) PRIMARY KEY,
        DJName NVARCHAR(200) NOT NULL,
        Equipment NVARCHAR(500) NULL,
        Region NVARCHAR(50) NOT NULL,
        Price DECIMAL(10,2) NULL,
        ContactPhone NVARCHAR(50) NULL,
        ContactEmail NVARCHAR(200) NULL
    );
END;

-- Catering
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Catering')
BEGIN
    CREATE TABLE dbo.Catering (
        CateringId INT IDENTITY(1,1) PRIMARY KEY,
        CateringName NVARCHAR(200) NOT NULL,
        CuisineType NVARCHAR(100) NULL,
        Region NVARCHAR(50) NOT NULL,
        PricePerPerson DECIMAL(10,2) NULL,
        Kosher BIT NOT NULL DEFAULT 0,
        ContactPhone NVARCHAR(50) NULL,
        ContactEmail NVARCHAR(200) NULL
    );
END;

-- Decor
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Decor')
BEGIN
    CREATE TABLE dbo.Decor (
        DecorId INT IDENTITY(1,1) PRIMARY KEY,
        DecorName NVARCHAR(200) NOT NULL,
        Style NVARCHAR(100) NULL,
        Region NVARCHAR(50) NOT NULL,
        Price DECIMAL(10,2) NULL,
        ContactPhone NVARCHAR(50) NULL,
        ContactEmail NVARCHAR(200) NULL
    );
END;

-- Photography
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Photography')
BEGIN
    CREATE TABLE dbo.Photography (
        PhotographyId INT IDENTITY(1,1) PRIMARY KEY,
        PhotographerName NVARCHAR(200) NOT NULL,
        PackageDescription NVARCHAR(500) NULL,
        Region NVARCHAR(50) NOT NULL,
        Price DECIMAL(10,2) NULL,
        ContactPhone NVARCHAR(50) NULL,
        ContactEmail NVARCHAR(200) NULL
    );
END;

-- Attractions
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Attraction')
BEGIN
    CREATE TABLE dbo.Attraction (
        AttractionId INT IDENTITY(1,1) PRIMARY KEY,
        AttractionName NVARCHAR(200) NOT NULL,
        AgeMin INT NULL,
        AgeMax INT NULL,
        Region NVARCHAR(50) NOT NULL,
        Price DECIMAL(10,2) NULL,
        Description NVARCHAR(500) NULL
    );
END;
"""


def main() -> None:
    db = DbGateway()
    db.execute(SCHEMA_SQL, commit=True)
    print("Polymorphic schema created successfully.")


if __name__ == "__main__":
    main()
