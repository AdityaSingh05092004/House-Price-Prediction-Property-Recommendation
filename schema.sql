CREATE DATABASE IF NOT EXISTS house_price_db;
USE house_price_db;

CREATE TABLE IF NOT EXISTS properties (
    property_id VARCHAR(32) PRIMARY KEY,
    city VARCHAR(100),
    locality VARCHAR(100),
    area_sqft INT,
    bedrooms INT,
    bathrooms INT,
    property_type VARCHAR(100),
    furnishing VARCHAR(100),
    parking INT,
    age_years INT,
    price_inr BIGINT
);
