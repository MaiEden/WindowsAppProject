"""
drop_all_tables.py
Wipes the database schema by dropping all foreign keys and all tables in the `dbo` schema.

WARNING:
- This operation is IRREVERSIBLE.
- It removes every foreign key and drops every table under `dbo`.
- Make a full backup before running, and ensure you're pointing to the correct database.
"""

from server.gateway.DBgateway import DbGateway

SQL = r"""
SET NOCOUNT ON;

-- 1) Drop all foreign keys so tables can be dropped without order constraints
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql = @sql + N'ALTER TABLE '
    + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + N'.' + QUOTENAME(OBJECT_NAME(parent_object_id))
    + N' DROP CONSTRAINT ' + QUOTENAME(name) + N';' + CHAR(10)
FROM sys.foreign_keys;
IF @sql <> N'' EXEC sp_executesql @sql;

-- 2) Drop all user tables in the dbo schema
SET @sql = N'';
SELECT @sql = @sql + N'DROP TABLE '
    + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(10)
FROM sys.tables
WHERE SCHEMA_NAME(schema_id) = 'dbo';
IF @sql <> N'' EXEC sp_executesql @sql;
"""


def main() -> None:
    """Execute the drop routine against the configured database connection."""
    db = DbGateway()
    db.execute(SQL, commit=True)
    print("All dbo tables dropped successfully.")

if __name__ == "__main__":
    main()
