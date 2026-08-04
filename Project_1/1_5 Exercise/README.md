SETUP:

1. Copy .env.example to a new file named .env
2. Fill in your own MySQL credentials (DB_USER, DB_PASS, DB_NAME, DB_HOST) and choose an API username/password (API_USER, API_PASS) - API_USER/API_PASS are required as Basic Auth credentials for POST /order, PUT /order/<id>, and POST /menu
3. Install dependencies: pip install -r requirements.txt
4. Run Create DATABASE.sql, then the other .sql files, to set up the database

SCHEMA NOTE:

The columns added to Create DATABASE.sql (menu_items.description, orders.status, orders.customer_name,
and making orders.customer_id/staff_id nullable with defaults on order_date/total_amount) were added
solely to fix the Flask API routes in flask 1e.py (e.g. POST /order, PUT /order/<id>) - they are not
part of, and are not needed for, the SQL queries.

In particular, orders.customer_name is separate from customers.name. It exists only to support
POST /order creating a quick order without a registered customer lookup, and will be NULL for all
seeded orders, which use the real customer_id foreign key instead. 

GUIDES USED:

1. DBUtils. (n.d.). PooledDB — DBUtils 3.1.2 documentation. Retrieved August 3, 2026, from https://webwareforpython.github.io/DBUtils/main.html

2. Flask-HTTPAuth Documentation. (n.d.). https://flask-httpauth.readthedocs.io/en/latest/getting-started.html#installation

3. W3Schools. (n.d.). SQL HAVING Clause. https://www.w3schools.com/sql/sql_having.asp

4. W3Schools. (n.d.-a). MySQL EXTRACT Function. https://www.w3schools.com/SQl/func_mysql_extract.asp

5. Hightouch. (2023). SQL COALESCE Function. https://hightouch.com/sql-dictionary/sql-coalesce