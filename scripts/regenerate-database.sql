DROP DATABASE IF EXISTS NYPLMenu;

CREATE DATABASE NYPLMenu;

USE NYPLMenu;

CREATE TABLE Dish (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    menus_appeared INT,
    times_appeared INT,
    first_appeared INT,
    last_appeared INT,
    lowest_price FLOAT,
    highest_price FLOAT
);

CREATE TABLE Menu (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    sponsor VARCHAR(255),
    event VARCHAR(255),
    venue VARCHAR(255),
    place VARCHAR(255),
    physical_description TEXT,
    occasion VARCHAR(255),
    notes TEXT,
    call_number VARCHAR(255),
    keywords TEXT,
    language VARCHAR(255),
    date DATE,
    location VARCHAR(255),
    location_type VARCHAR(255),
    currency VARCHAR(10),
    currency_symbol VARCHAR(5),
    status VARCHAR(50),
    page_count INT,
    dish_count INT
);

CREATE TABLE MenuPage (
    id INT PRIMARY KEY,
    menu_id INT,
    page_number INT,
    image_id INT,
    full_height INT,
    full_width INT,
    uuid CHAR(36),
    FOREIGN KEY (menu_id) REFERENCES Menu(id)
);

CREATE TABLE MenuItem (
    id INT PRIMARY KEY,
    menu_page_id INT,
    dish_id INT,
    price FLOAT,
    high_price FLOAT,
    created_at DATETIME,
    updated_at DATETIME,
    xpos FLOAT,
    ypos FLOAT,
    FOREIGN KEY (menu_page_id) REFERENCES MenuPage(id),
    FOREIGN KEY (dish_id) REFERENCES Dish(id)
);