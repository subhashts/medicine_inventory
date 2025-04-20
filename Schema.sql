-- Create database
CREATE DATABASE IF NOT EXISTS medicine_mgmt;
USE medicine_mgmt;

-- Remove existing tables (if any)
DROP TABLE IF EXISTS transaction;
DROP TABLE IF EXISTS medicine;
DROP TABLE IF EXISTS worker;
DROP TABLE IF EXISTS admin;

-- Create admin table
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

-- Create worker table
CREATE TABLE worker (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Create medicine table
CREATE TABLE medicine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    expiry_date DATE NOT NULL,
    price DECIMAL(10,2) DEFAULT 0
);

-- Create transaction table with proper constraints
CREATE TABLE transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    worker_id VARCHAR(10) NULL,
    quantity INT NOT NULL,
    type ENUM('buy', 'sell') NOT NULL,
    price DECIMAL(10,2) DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medicine_id) 
        REFERENCES medicine(id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) 
        REFERENCES worker(id) ON DELETE SET NULL
);