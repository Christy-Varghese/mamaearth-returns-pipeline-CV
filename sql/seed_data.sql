PRAGMA foreign_keys = ON;

-- Keep this loader re-runnable without changing the source CSV files.
DELETE FROM orders;
DELETE FROM products;
DELETE FROM customers;

.mode csv
.import --skip 1 data/customers.csv customers
.import --skip 1 data/products.csv products
.import --skip 1 data/orders.csv orders

-- SQLite's CSV importer represents blank cells as empty strings.
UPDATE orders
SET discount_pct = NULL
WHERE discount_pct = '';

UPDATE orders
SET rating = NULL
WHERE rating = '';