from flask import Flask, request, jsonify
import os, logging, pymysql #Added logging and pymysql for the try-catch blocks
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB #Added to fix Connection pooling issue

load_dotenv()

app = Flask(__name__)
#flaskext.mysql's MySQL()/init_app(app) removed: pool below is now the sole connection source

#For logging errors
logger = logging.getLogger(__name__)

#Repeated connection opening/closing fix
pool = PooledDB (
    creator=pymysql, #Driver used which DBUtils wraps 
    maxconnections=10, #cap on total connections used in the pool
    mincached=2, #Connections kept open & idle, ready to give to user(s)
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASS', ''),
    database=os.getenv('DB_NAME', 'restaurant_db'),
)

# Helper function with SQL injection vulnerability
def execute_query(query, params=None, return_id=False):
    conn = pool.connection() #Borrows a connection from the pol
    #Added a try-catch block
    try:
        cursor = conn.cursor()
        cursor.execute(query, params) #Security fix: Accepts params for safe, paramterised queries
        conn.commit() #required for INSERT/UPDATE/DELETE to actually persist
        #return_id added to fix "POST /order doesn't return the created order ID" (Functionality Bugs)
        if return_id:
            return cursor.lastrowid #id of the row just inserted, feature of pymysql, used to fix broken POST implementation 
        data = cursor.fetchall()
        return data
    except pymysql.err.Error as e:   #Only catches database-related errors this connection raises, more acurate than OSError
        logger.error(f"Database error: {e}")
        conn.rollback()   #Discard any uncommitted changes on failure, particularly handles proper transaction handling for creating_orders
        raise #Re-raise so calling route can build proper HTP error response
    finally:
        conn.close() 

# Route with insecure direct object reference
@app.route('/menu/<id>', methods=['GET'])
def get_menu_item(id):
    #Added a try-catch block
    try:
        #Security fix: Value passed separately and not concatenated into query string, prevents SQL injection
        query = "SELECT * FROM menu_items WHERE item_id = %s" #Schema fix: menu_items' primary key column is item_id, not id
        #id passed as tuple to fill the %s placeholder safely
        item = execute_query(query, (id,))
        if not item:
            return jsonify({"error": "Menu item not found"}), 404 #Missing HTTP Status code fix: Returns 404 instead of an empty 200 when no menu item matches the given id
        return jsonify(item)
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to get menu item"}), 500


# Route with missing error handling
@app.route('/menu', methods=['GET'])
def get_menu():
    #Added a try-catch block
    try:
        query = "SELECT * FROM menu_items"
        items = execute_query(query)
        return jsonify(items)
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to get menu"}), 500

# Route with broken POST implementation
@app.route('/order', methods=['POST'])
def create_order():
    #Added a try-catch block
    try:
        data = request.get_json()
        #Security fix: Customer name is passed separately, prevents SQL injection
        query = "INSERT INTO orders (customer_name) VALUES(%s)"
        #Input validation added, checks if user inputs a valid customer name
        if 'customer_name' in data:
            order_id = execute_query(query, (data['customer_name'],), return_id=True)  #return_id=True so we get the new order's id back to include in the response 
            return jsonify({"message": "Order created", "order_id": order_id}), 201
        else:
            return jsonify({"error": "Please input a valid customer name"}), 400
    except pymysql.err.Error as e: 
            logger.error(f"Database error: {e}")
            return jsonify({"error": "Unable to create order"}), 500

# Route with N+1 query problem
@app.route('/orders', methods=['GET'])
def get_orders():
    #Added a try-catch block
    try:
        #N+1 fix: single LEFT JOIN query replaces the old per-order loop that requests the DB once per order
        query = """
                SELECT orders.order_id, orders.customer_id, orders.staff_id, orders.order_date,
                    orders.total_amount, order_details.item_id, order_details.quantity, order_details.subtotal
                FROM orders
                LEFT JOIN order_details ON orders.order_id = order_details.order_id
                """
        rows = execute_query(query)

        #Groups the flat joined rows back into one entry per order, since a JOIN
        #returns one row per item (e.g an order with 3 items comes back as 3 rows)
        orders_dict = {}
        for row in rows:
            order_id, customer_id, staff_id, order_date, total_amount, item_id, quantity, subtotal = row

            if order_id not in orders_dict:
                orders_dict[order_id] = {
                    "order": (order_id, customer_id, staff_id, order_date, total_amount),
                    "items": []
                }

            #LEFT JOIN gives null item columns if order has no items, so skip adding a fake item
            if item_id is not None:
                orders_dict[order_id]["items"].append((item_id, quantity, subtotal))

        result = list(orders_dict.values())
        return jsonify(result)
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to get orders"}), 500

# Route with broken update
@app.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    #Added try-catch block
    try:
        data = request.get_json()
        #Input validation added, checks if order_id already exists in database
        check_query = "SELECT * FROM orders WHERE order_id = %s" #Schema fix: orders' primary key column is order_id, not id
        existing_order = execute_query(check_query, (order_id,))
        if not existing_order: 
                return jsonify({"error": "Order not found."}), 404
        #Security fix: Status and order id is passed separtely, prevents SQL injection
        query = "UPDATE orders SET status = %s WHERE order_id = %s" #Schema fix: orders' primary key column is order_id, not id
        #Input validation added, checks if user included status of order when checking for the specific order id
        if 'status' in data:
            execute_query(query, (data['status'], order_id),)
            return jsonify({"message": "Order updated"})
        else:
            return jsonify({"error": "Status field required"}), 400
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to update order"}), 500

# Route with missing authentication
@app.route('/menu', methods=['POST'])
def add_menu_item():
    #Aded try-catch block
    try:
        data = request.get_json()
        #Security fix: All values passed separely, prevents SQL injection
        query = "INSERT INTO menu_items (name, description, price, category) VALUES (%s, %s, %s, %s)"

        missing = []
        for field in ['name', 'description', 'price', 'category']:
            #Checks if all fields are present and spelt correctly 
            if field not in data:
                missing.append(field)

        #after ALL four fields have been checked, execute query
        if missing:
            return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

        execute_query(query, (data['name'], data['description'], data['price'], data['category'],))
        return jsonify({"message": "Menu item added"}), 201
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to add menu item"}), 500

if __name__ == '__main__':
    app.run(debug=True)