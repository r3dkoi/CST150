from flask import Flask, request, jsonify
from flaskext.mysql import MySQL
import os, logging, pymysql #Added logging and pymysql for the try-catch blocks
from dotenv import load_dotenv

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

# Helper function with SQL injection vulnerability
def execute_query(query, params=None):
    conn = mysql.connect()
    #Added a try-catch block
    try:
        cursor = conn.cursor()
        #Security fix: Accepts params for safe, paramterised queries
        cursor.execute(query, params)
        data = cursor.fetchall()
        return data
    #Only catches database-related errors this connection raises, more acurate than OSError
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
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
            execute_query(query, (data['customer_name'],))
            return jsonify({"message": "Order created"}), 201
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

        #Decision happens once, after ALL four fields have been checked
        if missing:
            return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

        execute_query(query, (data['name'], data['description'], data['price'], data['category'],))
        return jsonify({"message": "Menu item added"}), 201
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to add menu item"}), 500

if __name__ == '__main__':
    app.run(debug=True)