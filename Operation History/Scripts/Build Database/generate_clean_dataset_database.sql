DROP DATABASE IF EXISTS NYPLMenu;

CREATE DATABASE NYPLMenu;

USE NYPLMenu;

CREATE TABLE Dish (
    id INT,
    name TEXT,
    description TEXT,
    menus_appeared INT,
    times_appeared INT,
    first_appeared INT,
    last_appeared INT,
    lowest_price FLOAT,
    constant_price FLOAT,
    highest_price FLOAT
);

CREATE TABLE Menu (
    id INT,
    name VARCHAR(1024),
    sponsor TEXT,
    event VARCHAR(255),
    venue VARCHAR(255),
    place VARCHAR(255),
    highest_level_location TEXT,
    is_state BOOLEAN,
    physical_description TEXT,
    occasion VARCHAR(255),
    notes TEXT,
    call_number VARCHAR(255),
    keywords TEXT,
    language VARCHAR(255),
    date DATE,
    location VARCHAR(255),
    location_type VARCHAR(255),
    currency VARCHAR(255),
    currency_imputed VARCHAR(255),
    currency_symbol VARCHAR(5),
    status TEXT,
    page_count INT,
    dish_count INT
);

CREATE TABLE MenuPage (
    id INT,
    menu_id INT,
    page_number INT,
    image_id BIGINT,
    full_height INT,
    full_width INT,
    uuid CHAR(36)
);

CREATE TABLE MenuItem (
    id INT,
    menu_page_id INT,
    price FLOAT,
    price_imputed FLOAT,
    high_price FLOAT,
    dish_id INT,
    created_at DATETIME,
    updated_at DATETIME,
    xpos FLOAT,
    ypos FLOAT
);