"""
create_schema.py
Create the database schema for the Events app.
"""
from server.database.db_config import get_connection  # import your config

SCHEMA_SQL = """
--Create the schema if it doesn't exist
-- Users
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Users' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Users (
        UserId INT IDENTITY(1,1) PRIMARY KEY,
        Phone NVARCHAR(30) NOT NULL,
        Username NVARCHAR(100) NOT NULL UNIQUE,
        PasswordHash NVARCHAR(200) NOT NULL, -- demo only; hash properly in production
        Region NVARCHAR(50) NOT NULL
    );
END;

-- Services
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Services' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Services (
        ServiceId INT IDENTITY(1,1) PRIMARY KEY,
        ServiceType NVARCHAR(100) NOT NULL,
        ServiceDescription NVARCHAR(500) NULL,
        Region NVARCHAR(50) NOT NULL,
        MinAge INT NULL,
        MaxAge INT NULL,
        Price DECIMAL(10,2) NULL
    );
END;

-- Events
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='Events' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.Events (
        EventId INT IDENTITY(1,1) PRIMARY KEY,
        EventDate DATE NOT NULL,
        EventTime TIME(0) NOT NULL,
        EventType NVARCHAR(100) NOT NULL,
        ManagerUserId INT NOT NULL,
        CONSTRAINT FK_Events_Users_Manager FOREIGN KEY (ManagerUserId)
            REFERENCES dbo.Users(UserId)
    );
END;

-- Users <-> Services (which services a user offers)
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='UserServices' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.UserServices (
        UserId INT NOT NULL,
        ServiceId INT NOT NULL,
        CONSTRAINT PK_UserServices PRIMARY KEY (UserId, ServiceId),
        CONSTRAINT FK_US_User FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId) ON DELETE CASCADE,
        CONSTRAINT FK_US_Service FOREIGN KEY (ServiceId) REFERENCES dbo.Services(ServiceId) ON DELETE CASCADE
    );
END;

-- Events <-> Services (services planned/ordered for an event)
IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name='EventServices' AND schema_id = SCHEMA_ID('dbo'))
BEGIN
    CREATE TABLE dbo.EventServices (
        EventId INT NOT NULL,
        ServiceId INT NOT NULL,
        CONSTRAINT PK_EventServices PRIMARY KEY (EventId, ServiceId),
        CONSTRAINT FK_ES_Event FOREIGN KEY (EventId) REFERENCES dbo.Events(EventId) ON DELETE CASCADE,
        CONSTRAINT FK_ES_Service FOREIGN KEY (ServiceId) REFERENCES dbo.Services(ServiceId) ON DELETE CASCADE
    );
END;
"""

def main() -> None:
    with get_connection(autocommit=True) as conn:
        conn.cursor().execute(SCHEMA_SQL)
        print("Schema ensured (tables created as needed).")

if __name__ == "__main__":
    main()
