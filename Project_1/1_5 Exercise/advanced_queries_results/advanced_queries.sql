/* -------------------------------------------------------------------------- */
/*     Find customers who haven't placed any orders in the last 6 months.     */
/* -------------------------------------------------------------------------- */
/* Returned no rows because the 6-month window reaches back to 2023 but all the data 
in orders only fall between 2024-01 and 2024-03. */
SELECT customers.name
FROM customers
LEFT JOIN orders
    ON customers.customer_id = orders.customer_id
    AND orders.order_date >= (SELECT MAX(order_date) FROM orders) - INTERVAL 6 MONTH
WHERE orders.order_id IS NULL;

/* -------------------------------------------------------------------------- */
/*          Show the percentage of vegetarian items in each category.         */
/* -------------------------------------------------------------------------- */
SELECT category,
       SUM(is_vegetarian) AS vegetarian_count,
       COUNT(*) AS total_items,
       (SUM(is_vegetarian) / COUNT(*)) * 100 AS vegetarian_percentage
FROM menu_items
GROUP BY category;

/* -------------------------------------------------------------------------- */
/*   List staff members along with the total sales amount they've processed   */
/* -------------------------------------------------------------------------- */
SELECT staff.name, COALESCE(SUM(orders.total_amount), 0) AS total_sales
FROM staff
LEFT JOIN orders ON staff.staff_id = orders.staff_id
GROUP BY staff.staff_id;

/* -------------------------------------------------------------------------- */
/*                Find menu items that have never been ordered.               */
/* -------------------------------------------------------------------------- */
/* Returns no rows because all 15 menu items (item_id 1-15) appear at least
once in order_details.sql */
SELECT menu_items.name
FROM menu_items
LEFT JOIN order_details ON menu_items.item_id = order_details.item_id
WHERE order_details.order_detail_id IS NULL;

/* -------------------------------------------------------------------------- */
/*      Calculate the running total of sales for each day in January 2024     */
/* -------------------------------------------------------------------------- */
SELECT order_date_only,
    daily_total,
    SUM(daily_total) OVER (ORDER BY order_date_only) AS running_total
FROM (
    SELECT DATE(order_date) AS order_date_only, SUM(total_amount) AS daily_total
    FROM orders
    WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01'
    GROUP BY DATE(order_date)
) AS daily_sales
ORDER BY order_date_only;