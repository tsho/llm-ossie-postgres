-- TPC-DS Subset Schema for Apache Ossie Demo
-- This creates a simplified retail data model to demonstrate
-- how semantic metadata improves LLM-generated SQL accuracy.

-- Date Dimension
CREATE TABLE date_dim (
    d_date_sk INTEGER PRIMARY KEY,
    d_date DATE NOT NULL,
    d_year INTEGER NOT NULL,
    d_quarter_name VARCHAR(10),
    d_month_name VARCHAR(20)
);

-- Customer Dimension
CREATE TABLE customer (
    c_customer_sk INTEGER PRIMARY KEY,
    c_customer_id VARCHAR(20) NOT NULL,
    c_first_name VARCHAR(50),
    c_last_name VARCHAR(50),
    c_email_address VARCHAR(100)
);

-- Item/Product Dimension
CREATE TABLE item (
    i_item_sk INTEGER PRIMARY KEY,
    i_item_id VARCHAR(20) NOT NULL,
    i_item_desc VARCHAR(200),
    i_brand VARCHAR(50),
    i_category VARCHAR(50),
    i_current_price NUMERIC(7,2)
);

-- Store Dimension
CREATE TABLE store (
    s_store_sk INTEGER PRIMARY KEY,
    s_store_id VARCHAR(20) NOT NULL,
    s_store_name VARCHAR(100),
    s_city VARCHAR(60),
    s_state VARCHAR(2),
    s_number_employees INTEGER
);

-- Store Sales Fact
CREATE TABLE store_sales (
    ss_sold_date_sk INTEGER REFERENCES date_dim(d_date_sk),
    ss_item_sk INTEGER REFERENCES item(i_item_sk),
    ss_customer_sk INTEGER REFERENCES customer(c_customer_sk),
    ss_store_sk INTEGER REFERENCES store(s_store_sk),
    ss_quantity INTEGER,
    ss_sales_price NUMERIC(7,2),
    ss_ext_sales_price NUMERIC(7,2),
    ss_net_profit NUMERIC(7,2),
    ss_ticket_number INTEGER,
    PRIMARY KEY (ss_item_sk, ss_ticket_number)
);

-- Seed Data: Date Dimension (June 2024)
INSERT INTO date_dim VALUES
(1, '2024-06-01', 2024, '2024Q2', 'June'),
(2, '2024-06-05', 2024, '2024Q2', 'June'),
(3, '2024-06-10', 2024, '2024Q2', 'June'),
(4, '2024-06-15', 2024, '2024Q2', 'June'),
(5, '2024-06-20', 2024, '2024Q2', 'June'),
(6, '2024-06-25', 2024, '2024Q2', 'June'),
(7, '2024-06-30', 2024, '2024Q2', 'June'),
(8, '2024-07-01', 2024, '2024Q3', 'July'),
(9, '2024-07-05', 2024, '2024Q3', 'July'),
(10, '2024-07-10', 2024, '2024Q3', 'July'),
(11, '2024-07-15', 2024, '2024Q3', 'July'),
(12, '2024-07-20', 2024, '2024Q3', 'July'),
(13, '2024-07-25', 2024, '2024Q3', 'July'),
(14, '2024-07-31', 2024, '2024Q3', 'July');

-- Seed Data: Customers
INSERT INTO customer VALUES
(1, 'CUST001', 'Alice', 'Johnson', 'alice.j@example.com'),
(2, 'CUST002', 'Bob', 'Smith', 'bob.s@example.com'),
(3, 'CUST003', 'Carol', 'Williams', 'carol.w@example.com'),
(4, 'CUST004', 'David', 'Brown', 'david.b@example.com'),
(5, 'CUST005', 'Eve', 'Davis', 'eve.d@example.com');

-- Seed Data: Items
INSERT INTO item VALUES
(1, 'ITEM001', 'Wireless Bluetooth Headphones', 'Sony', 'Electronics', 79.99),
(2, 'ITEM002', 'Organic Coffee Beans 1kg', 'Starbucks', 'Grocery', 24.99),
(3, 'ITEM003', 'Running Shoes Size 10', 'Nike', 'Footwear', 129.99),
(4, 'ITEM004', 'Stainless Steel Water Bottle', 'Hydro Flask', 'Home', 34.99),
(5, 'ITEM005', 'USB-C Charging Cable 2m', 'Anker', 'Electronics', 14.99),
(6, 'ITEM006', 'Yoga Mat Premium', 'Lululemon', 'Sports', 68.00),
(7, 'ITEM007', 'Instant Ramen Variety Pack', 'Nissin', 'Grocery', 12.99),
(8, 'ITEM008', 'Leather Wallet', 'Coach', 'Accessories', 89.99);

-- Seed Data: Stores
INSERT INTO store VALUES
(1, 'STORE01', 'Downtown Flagship', 'San Francisco', 'CA', 45),
(2, 'STORE02', 'Mall of America', 'Minneapolis', 'MN', 32),
(3, 'STORE03', 'Brooklyn Heights', 'New York', 'NY', 28);

-- Seed Data: Store Sales (June-July 2024)
-- Note: ss_ext_sales_price = ss_quantity * ss_sales_price
-- ss_net_profit is after cost deduction (varies by item)
INSERT INTO store_sales VALUES
-- June sales
(1, 1, 1, 1, 2, 79.99, 159.98, 40.00, 1001),
(1, 2, 2, 1, 3, 24.99, 74.97, 30.00, 1002),
(2, 3, 3, 2, 1, 129.99, 129.99, 35.00, 1003),
(2, 5, 1, 1, 4, 14.99, 59.96, 28.00, 1004),
(3, 4, 4, 3, 2, 34.99, 69.98, 25.00, 1005),
(3, 6, 5, 2, 1, 68.00, 68.00, 20.00, 1006),
(4, 1, 2, 1, 1, 79.99, 79.99, 20.00, 1007),
(4, 7, 3, 3, 5, 12.99, 64.95, 22.00, 1008),
(5, 8, 1, 1, 1, 89.99, 89.99, 35.00, 1009),
(5, 2, 4, 2, 2, 24.99, 49.98, 20.00, 1010),
(6, 3, 5, 3, 1, 129.99, 129.99, 35.00, 1011),
(6, 5, 2, 1, 3, 14.99, 44.97, 21.00, 1012),
(7, 4, 1, 2, 2, 34.99, 69.98, 25.00, 1013),
(7, 6, 3, 3, 1, 68.00, 68.00, 20.00, 1014),
-- July sales
(8, 1, 1, 1, 3, 79.99, 239.97, 60.00, 2001),
(8, 2, 2, 2, 4, 24.99, 99.96, 40.00, 2002),
(9, 3, 4, 1, 2, 129.99, 259.98, 70.00, 2003),
(9, 7, 5, 3, 6, 12.99, 77.94, 26.00, 2004),
(10, 8, 3, 2, 1, 89.99, 89.99, 35.00, 2005),
(10, 5, 1, 1, 5, 14.99, 74.95, 35.00, 2006),
(11, 6, 2, 2, 2, 68.00, 136.00, 40.00, 2007),
(11, 4, 4, 3, 3, 34.99, 104.97, 37.00, 2008),
(12, 1, 5, 1, 1, 79.99, 79.99, 20.00, 2009),
(12, 3, 1, 2, 1, 129.99, 129.99, 35.00, 2010),
(13, 2, 3, 3, 2, 24.99, 49.98, 20.00, 2011),
(13, 8, 2, 1, 1, 89.99, 89.99, 35.00, 2012),
(14, 5, 4, 2, 4, 14.99, 59.96, 28.00, 2013),
(14, 7, 5, 3, 3, 12.99, 38.97, 13.00, 2014);
