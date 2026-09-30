.headers on
.mode column

-- 3(a) Output: total_orders = 180, total_revenue = 99860.20, avg_order_value = 554.78
SELECT
	COUNT(*) AS total_orders,
	ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
	ROUND(AVG(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS avg_order_value
FROM orders AS o
JOIN products AS p ON p.product_id = o.product_id;


-- 3(b) Output: total_rows = 180, rated_rows = 165, unrated_rows = 15
SELECT 
	COUNT(*) AS total_rows,
	COUNT(rating) AS rated_rows,
	COUNT(*) - COUNT(rating) AS unrated_rows
FROM orders;

-- 3(c) Output: C045 | Vihaan
SELECT c.customer_id, c.name
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

-- 3(c) Independent check output: C045 | Vihaan
SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (SELECT DISTINCT customer_id FROM orders);

-- 3(d) Output:
-- Jaipur | 19 | 8 | 42.1
-- Lucknow | 49 | 15 | 30.6
-- Bangalore | 33 | 8 | 24.2
SELECT
	c.city,
	COUNT(*) AS total_orders,
	SUM(o.returned) AS returned_orders,
	ROUND(100.0 * SUM(o.returned) / COUNT(*), 1) AS return_rate_pct
FROM orders AS o
JOIN customers AS c ON c.customer_id = o.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

-- 3(e) The customer_id tie-breaker makes ranking deterministic when customers have equal spend.
-- 3(e) LIMIT 5 output:
-- C043 | Reyansh | 12920.00
-- C026 | Isha | 8371.60
-- C008 | Meera | 4564.60
-- C011 | Arjun | 4111.00
-- C042 | Sanya | 3785.00
SELECT
	c.customer_id,
	c.name,
	ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders AS o
JOIN products AS p ON p.product_id = o.product_id
JOIN customers AS c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;

-- 3(e) LIMIT 3 OFFSET 2 output:
-- C008 | Meera | 4564.60
-- C011 | Arjun | 4111.00
-- C042 | Sanya | 3785.00
SELECT
	c.customer_id,
	c.name,
	ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders AS o
JOIN products AS p ON p.product_id = o.product_id
JOIN customers AS c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;

-- 3(f) Output:
-- Haircare | 54 | 44956.10
-- Skincare | 60 | 27346.00
-- Babycare | 30 | 16805.00
-- PersonalCare | 36 | 10753.10
SELECT
	p.category,
	COUNT(*) AS order_count,
	ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders AS o
JOIN products AS p ON p.product_id = o.product_id
JOIN customers AS c ON c.customer_id = o.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- 3(g) Output:
-- C001 | Aarav
-- C003 | Aditi
-- C004 | Ananya
-- C011 | Arjun
-- C021 | Aryan
-- C030 | Anika
-- C031 | Aditya
-- C036 | Aisha
-- C041 | Ayaan
-- C044 | Aria
SELECT customer_id, name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;

-- 3(h) Output: Ad, Organic, Referral, Social
SELECT DISTINCT acquisition_source
FROM customers
ORDER BY acquisition_source;

-- 3(i) Add and populate the loyalty tier for every customer.
ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier = CASE
	WHEN city_tier = 1 THEN 'Gold'
	ELSE 'Silver'
END;

-- 3(i) Output: Gold | 28, Silver | 17
SELECT loyalty_tier, COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;