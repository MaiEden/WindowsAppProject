# archive/EasyEventPlanningDBInserts/drop_all_tables.py
"""
drop_all_tables.py
Drops all user tables in the current database after removing foreign keys.
IRREVERSIBLE. Make a backup or be sure you want to wipe the schema.
"""

from DataBase.db_config import get_connection

SQL = r"""
SET NOCOUNT ON;

-- 1) Drop all foreign keys (so tables can be dropped in any order)
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql = @sql + N'ALTER TABLE '
    + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + N'.' + QUOTENAME(OBJECT_NAME(parent_object_id))
    + N' DROP CONSTRAINT ' + QUOTENAME(name) + N';' + CHAR(10)
FROM sys.foreign_keys;
IF @sql <> N'' EXEC sp_executesql @sql;

-- 2) Drop all user tables in dbo schema (adjust schema if needed)
SET @sql = N'';
SELECT @sql = @sql + N'DROP TABLE '
    + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(10)
FROM sys.tables
WHERE SCHEMA_NAME(schema_id) = 'dbo';
IF @sql <> N'' EXEC sp_executesql @sql;
"""

def main() -> None:
    with get_connection(autocommit=True) as conn:
        cur = conn.cursor()
        cur.execute(SQL)
        print("All dbo tables dropped successfully.")

if __name__ == "__main__":
    main()
