/* -------------------------------------------------------------------------- */
/*                1.  Find the top 5 most expensive menu items.               */
/* -------------------------------------------------------------------------- */
SELECT name, price FROM menu_items
ORDER BY price DESC
LIMIT 5;

/* -------------------------------------------------------------------------- */
/*             2.  Calculate the average price of all menu items.             */
/* -------------------------------------------------------------------------- */
SELECT AVG(price) from menu_items;

/* -------------------------------------------------------------------------- */
/*        3.  Calculate the average order total amount for March 2024.        */
/* -------------------------------------------------------------------------- */
SELECT AVG(total_amount) FROM orders
WHERE order_date BETWEEN '2024-3-1' AND '2024-3-31';

/* -------------------------------------------------------------------------- */
/*             4.  Show how many menu items are in each category.             */
/* -------------------------------------------------------------------------- */
SELECT category, COUNT(*) AS "No. in Each Category"
FROM menu_items
GROUP BY category;
/* -------------------------------------------------------------------------- */
/*        5.  Find the total sales amount for each day in January 2024.       */
/* -------------------------------------------------------------------------- */
SELECT DATE(order_date), SUM(total_amount) AS "Total sales"
FROM orders
WHERE order_date BETWEEN '2024-1-1' AND '2024-1-31'
GROUP BY DATE(order_date);

/* -------------------------------------------------------------------------- */
/*   6.  List all order details where the quantity ordered was more than 1.   */
/* -------------------------------------------------------------------------- */
SELECT order_detail_id, quantity FROM order_details
WHERE quantity > 1;



/* 7.  Show customers who joined in the last 12 months (from current date). */
SELECT name, join_date FROM customers
WHERE join_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);

SELECT CURDATE();
/* -------------------------------------------------------------------------- */
/*    8.  List all staff positions and how many people hold each position.    */
/* -------------------------------------------------------------------------- */
SELECT position, COUNT(*) AS "Number of Staff in Position"
FROM staff
GROUP BY position;