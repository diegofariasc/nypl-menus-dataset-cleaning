-- View all tables and row count
SELECT
    table_name,
    table_rows
FROM
    information_schema.tables
WHERE
    table_schema = 'NYPLMenu'
    AND table_type = 'BASE TABLE';