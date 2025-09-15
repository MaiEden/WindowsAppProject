
"""
migrate_remove_events.py
Safely remove ONLY legacy Event-related tables (Event, EventService) and the old polymorphic UserService table.
Does NOT touch Users, Hall, DecorOption, ServiceOption, or any other data.

Run:
    python migrate_remove_events.py
"""
from server.gateway.DBgateway import DbGateway

SQL = r"""
SET NOCOUNT ON;

-- Drop foreign keys that reference the legacy tables (if any)
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql = @sql + N'ALTER TABLE '
    + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + N'.' + QUOTENAME(OBJECT_NAME(parent_object_id))
    + N' DROP CONSTRAINT ' + QUOTENAME(name) + N';' + CHAR(10)
FROM sys.foreign_keys
WHERE referenced_object_id IN (
    OBJECT_ID(N'dbo.Event'),
    OBJECT_ID(N'dbo.EventService'),
    OBJECT_ID(N'dbo.UserService')
);
IF @sql <> N'' EXEC sp_executesql @sql;

-- Drop the legacy tables if they exist
IF OBJECT_ID(N'dbo.EventService', N'U') IS NOT NULL DROP TABLE dbo.EventService;
IF OBJECT_ID(N'dbo.Event', N'U')         IS NOT NULL DROP TABLE dbo.Event;
IF OBJECT_ID(N'dbo.UserService', N'U')   IS NOT NULL DROP TABLE dbo.UserService;
"""

def main() -> None:
    db = DbGateway()
    db.execute(SQL, commit=True)
    print("Removed legacy tables: Event, EventService, UserService (if existed).")

if __name__ == "__main__":
    main()
