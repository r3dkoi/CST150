/* -------------------------------------------------------------------------- */
/*             Query 1: List all customers alphabetically by name             */
/* -------------------------------------------------------------------------- */
SELECT name FROM customers
ORDER BY name ASC

/* -------------------------------------------------------------------------- */
/*           Query 2: List all menu items with prices less than $10           */
/*                         ordered by Price ascending
-------------------------------------------------------------------------- */
SELECT name FROM menu_items
WHERE price < 10.00
ORDER by price ASC
