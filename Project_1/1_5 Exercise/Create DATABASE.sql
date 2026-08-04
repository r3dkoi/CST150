CREATE DATABASE restaurant_db;
USE restaurant_db;

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    join_date DATE NOT NULL
);

CREATE TABLE menu_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255) NULL, -- Added to match what POST /menu actually inserts
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    is_vegetarian BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) NOT NULL
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NULL, -- Made nullable: POST /order only takes customer_name, no customer_id lookup
    staff_id INT NULL, -- Made nullable: no staff assigned yet at order-creation time
    customer_name VARCHAR(100) NULL, -- Added to match what POST /order actually inserts
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- Auto-filled so the client doesn't need to send it
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00, -- Starts at 0, updated later as items are added
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- Added so PUT /order/<id> has a real column to update
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);

CREATE TABLE order_details (
    order_detail_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

-- Then run all the INSERT statements above