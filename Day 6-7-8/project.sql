-- Database: Infinite

-- DROP DATABASE IF EXISTS "Infinite";

CREATE DATABASE "Infinite"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_India.1252'
    LC_CTYPE = 'English_India.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;



DROP TABLE IF EXISTS sales;

CREATE TABLE sales (
    customer_id         INTEGER,
    order_id            INTEGER,
    product_category    VARCHAR(100),
    product             VARCHAR(255),
    quantity_ordered    INTEGER,
    price_each          VARCHAR(30),
    order_date          VARCHAR(50),
    purchase_address    TEXT,
    sales               VARCHAR(30),
    city                VARCHAR(100),
    hour                INTEGER,
    time_of_day         VARCHAR(20)
);

select * from sales;

SELECT * FROM sales;

-- Display top 5 rows
SELECT *
FROM sales
LIMIT 5;

-- Describe table
SELECT column_name,
       data_type,
       is_nullable
FROM information_schema.columns
WHERE table_name = 'sales';

-- Distinct values
SELECT DISTINCT time_of_day
FROM sales;

-------------------------------------------------------
-- Sales city wise
-------------------------------------------------------

SELECT city,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
FROM sales
GROUP BY city;

SELECT city,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
FROM sales
GROUP BY city
ORDER BY total_sales DESC;

-------------------------------------------------------
-- Total Sales by Product Category
-------------------------------------------------------

SELECT product_category,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
FROM sales
GROUP BY product_category
ORDER BY total_sales DESC;

-------------------------------------------------------
-- Sales by Time of Day
-------------------------------------------------------

SELECT time_of_day,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
FROM sales
GROUP BY time_of_day
ORDER BY total_sales DESC;

-------------------------------------------------------
-- Number of Orders Per City
-------------------------------------------------------

SELECT city,
       COUNT(order_id) AS number_of_orders
FROM sales
GROUP BY city
ORDER BY number_of_orders DESC;

-------------------------------------------------------
-- Sales by Hour
-------------------------------------------------------

SELECT hour,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
FROM sales
GROUP BY hour
ORDER BY total_sales DESC;

-------------------------------------------------------
-- Hour with Maximum Sales
-------------------------------------------------------

SELECT hour,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
FROM sales
GROUP BY hour
ORDER BY total_sales DESC
LIMIT 1;

-------------------------------------------------------
-- Second Highest
-------------------------------------------------------

SELECT hour,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
FROM sales
GROUP BY hour
ORDER BY total_sales DESC
OFFSET 1
LIMIT 1;

-------------------------------------------------------
-- Count per Product Category
-------------------------------------------------------

SELECT product_category,
       COUNT(*) AS count
FROM sales
GROUP BY product_category
ORDER BY count DESC;

-------------------------------------------------------
-- Top 3 Product Categories
-------------------------------------------------------

SELECT product_category,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_revenue
FROM sales
GROUP BY product_category
ORDER BY total_revenue DESC
LIMIT 3;

-------------------------------------------------------
-- Revenue from Top 3 Categories
-------------------------------------------------------

SELECT SUM(total_sales) AS total_revenue
FROM
(
    SELECT product_category,
           SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
    FROM sales
    GROUP BY product_category
    ORDER BY total_sales DESC
    LIMIT 3
) t;

-------------------------------------------------------
-- Sales in 2019
-------------------------------------------------------

SELECT product_category,
       SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS total_sales
FROM sales
WHERE EXTRACT(YEAR FROM order_date_changed)=2019
GROUP BY product_category
ORDER BY total_sales DESC;

-------------------------------------------------------
-- Overall Sales 2019
-------------------------------------------------------

SELECT SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS overall_sales
FROM sales
WHERE EXTRACT(YEAR FROM order_date_changed)=2019;

-------------------------------------------------------
-- Percentage Contribution
-------------------------------------------------------

WITH total_sales_2019 AS
(
    SELECT SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS overall_sales
    FROM sales
    WHERE EXTRACT(YEAR FROM order_date_changed)=2019
),

category_sales AS
(
    SELECT product_category,
           SUM(REPLACE(REPLACE(sales, '$', ''), ',', '')::numeric) AS category_total
    FROM sales
    WHERE EXTRACT(YEAR FROM order_date_changed)=2019
    GROUP BY product_category
)

SELECT
    cs.product_category,
    cs.category_total,
    ROUND((cs.category_total/ts.overall_sales)*100,2) AS percentage_contribution
FROM category_sales cs
CROSS JOIN total_sales_2019 ts;

-------------------------------------------------------
-- Widest Price Range
-------------------------------------------------------

SELECT
    product_category,
    MAX(REPLACE(REPLACE(price_each,'$',''),',','')::numeric) -
    MIN(REPLACE(REPLACE(price_each,'$',''),',','')::numeric) AS price_range
FROM sales
GROUP BY product_category
ORDER BY price_range DESC
LIMIT 1;

-------------------------------------------------------
-- Category with Highest Total Sales
-------------------------------------------------------

SELECT
    SUM(REPLACE(REPLACE(sales,'$',''),',','')::numeric) AS total_sales
FROM sales
WHERE product_category =
(
    SELECT product_category
    FROM
    (
        SELECT
            product_category,
            SUM(REPLACE(REPLACE(sales,'$',''),',','')::numeric) AS category_total
        FROM sales
        GROUP BY product_category
        ORDER BY category_total DESC
        LIMIT 1
    ) t
);

-------------------------------------------------------
-- Products Above Average Price
-------------------------------------------------------

SELECT product
FROM sales
WHERE REPLACE(REPLACE(price_each,'$',''),',','')::numeric >
(
    SELECT AVG(REPLACE(REPLACE(price_each,'$',''),',','')::numeric)
    FROM sales
);

-------------------------------------------------------
-- Lowest Selling Category
-------------------------------------------------------

SELECT product_category
FROM
(
    SELECT
        product_category,
        SUM(REPLACE(REPLACE(sales,'$',''),',','')::numeric) AS total_sales
    FROM sales
    GROUP BY product_category
    ORDER BY total_sales
    LIMIT 1
) t;

-------------------------------------------------------
-- Customers Purchasing Above Average Quantity
-------------------------------------------------------

SELECT *
FROM sales
WHERE customer_id IN
(
    SELECT customer_id
    FROM sales
    GROUP BY customer_id
    HAVING SUM(quantity_ordered) >
    (
        SELECT AVG(total_quantity)
        FROM
        (
            SELECT
                customer_id,
                SUM(quantity_ordered) AS total_quantity
            FROM sales
            GROUP BY customer_id
        ) t
    )
);

-------------------------------------------------------
-- Products Cheaper than Cheapest Laptop
-------------------------------------------------------

SELECT product
FROM sales
WHERE REPLACE(REPLACE(price_each,'$',''),',','')::numeric <
(
    SELECT MIN(REPLACE(REPLACE(price_each,'$',''),',','')::numeric)
    FROM sales
    WHERE product_category='Laptops and Computers'
);

-------------------------------------------------------
-- CTE: Total Sales by Category
-------------------------------------------------------

WITH category_sales AS
(
    SELECT
        product_category,
        SUM(REPLACE(REPLACE(sales,'$',''),',','')::numeric) AS total_sales
    FROM sales
    GROUP BY product_category
)
SELECT *
FROM category_sales;

-------------------------------------------------------
-- Average Sales per Category
-------------------------------------------------------

WITH category_sales AS
(
    SELECT
        product_category,
        AVG(REPLACE(REPLACE(sales,'$',''),',','')::numeric) AS total_sales
    FROM sales
    GROUP BY product_category
)

SELECT AVG(total_sales)
FROM category_sales;

-------------------------------------------------------
-- Top Selling Category using CTE
-------------------------------------------------------

WITH category_sales AS
(
    SELECT
        product_category,
        SUM(REPLACE(REPLACE(sales,'$',''),',','')::numeric) AS total_sales
    FROM sales
    GROUP BY product_category
)

SELECT product_category
FROM category_sales
ORDER BY total_sales DESC
LIMIT 1;


select * from sales;



copy sales
FROM 'C:\Users\Abhishek\Desktop\Infinite\sql\SalesDataAnalysis.csv'
DELIMITER ','
CSV HEADER;






SELECT COUNT(*) FROM sales;






