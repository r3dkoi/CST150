USE restaurant_db;

-- Adds description column to menu_items (needed for POST /menu)
ALTER TABLE menu_items
    ADD COLUMN description VARCHAR(255) NULL AFTER name;

-- Adds status column to orders (needed for PUT /order/<id>)
ALTER TABLE orders
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending';

-- Adds customer_name column to orders (needed for POST /order)
ALTER TABLE orders
    ADD COLUMN customer_name VARCHAR(100) NULL AFTER staff_id;

-- Makes customer_id and staff_id optional, since POST /order only provides customer_name
ALTER TABLE orders
    MODIFY COLUMN customer_id INT NULL,
    MODIFY COLUMN staff_id INT NULL;

-- Gives order_date and total_amount defaults, since POST /order doesn't provide them
ALTER TABLE orders
    MODIFY COLUMN order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    MODIFY COLUMN total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00;
