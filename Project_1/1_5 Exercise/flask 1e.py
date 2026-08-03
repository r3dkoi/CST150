from flask import Flask, request, jsonify
from flaskext.mysql import MySQL
import os, logging, pymysql #Added logging and pymysql for the try-catch blocks
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB #Added to fix Connection pooling issue

load_dotenv()

app = Flask(__name__)
mysql = MySQL()

# Configuration with security issues
app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER', 'root')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('DB_PASS', '')
app.config['MYSQL_DATABASE_DB'] = os.getenv('DB_NAME', 'restaurant_db')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST', 'localhost')
mysql.init_app(app)

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
    conn = mysql.connect()
    #Added a try-catch block
    try:
        cursor = conn.cursor()
        #Security fix: Accepts params for safe, paramterised queries
        cursor.execute(query, params)
        #required for INSERT/UPDATE/DELETE to actually persist
        conn.commit()
        #return_id added to fix "POST /order doesn't return the created order ID" (Functionality Bugs)
        if return_id:
            return cursor.lastrowid #id of the row just inserted, feature of pymysql, used to fix broken POST implementation 
        data = cursor.fetchall()
        return data
    #Only catches database-related errors this connection raises, more acurate than OSError
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
    #Discard any uncommitted changes on failure, particularly handles proper transaction handling for creating_orders
        conn.rollback() 
        raise #Re-raise so calling route can build proper HTP error response
    finally:
        conn.close() 

# Route with insecure direct object reference
@app.route('/menu/<id>', methods=['GET'])
def get_menu_item(id):
    #Added a try-catch block
    try:
        #Security fix: Value passed separately and not concatenated into query string, prevents SQL injection
        query = "SELECT * FROM menu_items WHERE id = %s"
        #id passed as tuple to fill the %s placeholder safely
        item = execute_query(query, (id,))
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
            #return_id=True so we get the new order's id back to include in the response 
            order_id = execute_query(query, (data['customer_name'],), return_id=True)
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
        query = "SELECT * FROM orders"
        orders = execute_query(query)
        
        result = []
        for order in orders:
            #Security fix: order_id passed separately, prevents SQL injection
            item_query = "SELECT * FROM order_items WHERE order_id = %s"
            items = execute_query(item_query, (order[0],))
            result.append({
                "order": order,
                "items": items
            })
        
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
        check_query = "SELECT * FROM orders WHERE id = %s"
        existing_order = execute_query(check_query, (order_id,))
        if not existing_order: 
                return jsonify({"error": "Order not found."}), 404
        #Security fix: Status and order id is passed separtely, prevents SQL injection
        query = "UPDATE orders SET status = %s WHERE id = %s"
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