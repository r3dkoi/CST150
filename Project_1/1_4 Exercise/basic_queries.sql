/* -------------------------------------------------------------------------- */
/*             Query 1: List all customers alphabetically by name             */
/* -------------------------------------------------------------------------- */
SELECT name FROM customers
ORDER BY name ASC;

/* -------------------------------------------------------------------------- */
/*           Query 2: List all menu items with prices less than $10           */
/*  ------------------------------  ordered by Price ascending  ------------------------ */
SELECT name FROM menu_items
WHERE price < 10.00
ORDER BY price ASC;

/* -------------------------------------------------------------------------- */
/*     Query 3: Find all customers who joined in 2023, sorted by join date    */
/* -------------------------------------------------------------------------- */
SELECT name, join_date FROM customers
WHERE YEAR(join_date) =  2023
ORDER BY join_date ASC;

/* -------------------------------------------------------------------------- */
/*    4.  Show the total number of vegetarian items available on the menu.    */
/* -------------------------------------------------------------------------- */
SELECT COUNT(*) FROM menu_items
WHERE is_vegetarian = 1;

/* -------------------------------------------------------------------------- */
/*           5.  List all beverages sorted by price (lowest first).           */
/* -------------------------------------------------------------------------- */
SELECT category, price FROM menu_items
WHERE category = 'Beverages'
ORDER BY price ASC;

/* 6.  Display all orders placed on January 1, 2024 with their total amounts. */
SELECT order_id, order_date, total_amount FROM orders
WHERE DATE(order_date) = '2024-01-1';


/* -------------------------------------------------------------------------- */
/*            7.  Show orders with total amounts between 20 and 30.           */
/* -------------------------------------------------------------------------- */
SELECT order_id, total_amount FROM orders
WHERE total_amount BETWEEN 20.00 AND 30.00;


/* 8.  List all staff members who are chefs, sorted by hire date (newest first) */
SELECT name, position, hire_date FROM staff
WHERE position LIKE '%Chef%'
ORDER BY hire_date DESC;

