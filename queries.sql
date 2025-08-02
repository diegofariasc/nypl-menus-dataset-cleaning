-- View all tables and row count
SELECT
    table_name,
    table_rows
FROM
    information_schema.tables
WHERE
    table_schema = 'NYPLMenu'
    AND table_type = 'BASE TABLE';

-- Detect null or empty dish_id values in MenuItem dataset
SELECT
    COUNT(*)
FROM
    MenuItem
WHERE
    dish_id IS NULL;

-- Detect outliers or null date value in Menu dataset
SELECT
    COUNT(*)
FROM
    Menu
WHERE
    YEAR(date) < 1958
    OR YEAR(date) > 2025
    OR date IS NULL;

-- Get result for main use case
SELECT
    COUNT(*)
FROM
    (
        SELECT
            Menu.id,
            Menu.date,
            Dish.name,
            MenuItem.price,
            MenuItem.created_at,
            MenuItem.updated_at
        FROM
            Menu
            JOIN MenuPage ON Menu.id = MenuPage.menu_id
            JOIN MenuItem ON MenuPage.id = MenuItem.menu_page_id
            JOIN Dish ON MenuItem.dish_id = Dish.id
    ) UseCaseData;