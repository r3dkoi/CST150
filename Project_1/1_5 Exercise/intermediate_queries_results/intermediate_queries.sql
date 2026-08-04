/* -------------------------------------------------------------------------- */
/*            1. List customers who have placed more than 5 orders,           */
/*                        along with their order count.                       */
/* -------------------------------------------------------------------------- */

/* Since the database I am using actually doesn't have any orders > 5, I changed it to >= 3 for results. */
SELECT name, COUNT(orders.order_id) AS order_count
FROM customers
JOIN orders ON customers.customer_id = orders.customer_id
GROUP BY customers.customer_id
HAVING order_count >= 3;

/* -------------------------------------------------------------------------- */
/*         Show the most popular menu item (most frequently ordered).         */
/* -------------------------------------------------------------------------- */
SELECT name, COUNT(*) AS most_popular
FROM menu_items
JOIN order_details ON menu_items.item_id = order_details.item_id
GROUP BY menu_items.item_id
ORDER BY most_popular DESC
LIMIT 1;

/* -------------------------------------------------------------------------- */
/*             Calculate the total revenue for each month in 2024             */
/* -------------------------------------------------------------------------- */
SELECT EXTRACT(MONTH FROM order_date) AS month, SUM(total_amount) AS total_revenue
FROM orders
WHERE EXTRACT(YEAR FROM order_date) = 2024
GROUP BY EXTRACT(MONTH FROM order_date);


