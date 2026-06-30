-- Create Database
CREATE DATABASE IF NOT EXISTS financial_lake;
USE financial_lake;

-- Create SCD Type 2 Customer Dimension Table
CREATE TABLE dim_customer (
    customer_id INT,
    first_name STRING,
    last_name STRING,
    risk_segment STRING,
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN
)
STORED AS PARQUET;

-- Create Partitioned Transaction Fact Table
CREATE TABLE fact_transaction (
    transaction_id STRING,
    customer_id INT,
    transaction_date TIMESTAMP,
    amount DOUBLE,
    currency STRING,
    transaction_type STRING
)
PARTITIONED BY (transaction_year INT, transaction_month INT)
STORED AS PARQUET;

-- Insert Customer Records
INSERT INTO TABLE dim_customer VALUES 
    (1001, 'Omar', 'Farooq', 'LOW', '2023-01-15', '2025-12-31', true),
    (1002, 'Sarah', 'Ahmed', 'MEDIUM', '2024-03-22', '2025-12-31', true);

-- Allow Dynamic Partition Inserts
SET hive.exec.dynamic.partition.mode=nonstrict;

-- Insert Partitioned Transaction Records
INSERT INTO TABLE fact_transaction PARTITION (transaction_year, transaction_month) VALUES 
    ('TXN-9901', 1001, '2026-06-15 10:30:00', 1500.50, 'AED', 'DEPOSIT', 2026, 6),
    ('TXN-9902', 1002, '2026-06-16 14:45:00', -350.00, 'AED', 'WITHDRAWAL', 2026, 6);