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
SELECT name FROM customers
WHERE YEAR(join_date) =  2023
ORDER BY join_date ASC;