from flask import Flask, request, jsonify
from flaskext.mysql import MySQL
import os
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

# Helper function with SQL injection vulnerability
def execute_query(query, params=None):
    conn = mysql.connect()
    cursor = conn.cursor()
    #Security fix: Accepts params for safe, paramterised queries
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data

# Route with insecure direct object reference
@app.route('/menu/<id>', methods=['GET'])
def get_menu_item(id):
    #Security fix: Value passed separately and not concatenated into query string, prevents SQL injection
    query = "SELECT * FROM menu_items WHERE id = %s"
    item = execute_query(query, (id,))
    return jsonify(item)

# Route with missing error handling
@app.route('/menu', methods=['GET'])
def get_menu():
    query = "SELECT * FROM menu_items"
    items = execute_query(query)
    return jsonify(items)

# Route with broken POST implementation
@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    query = f"INSERT INTO orders (customer_name) VALUES ('{data['customer_name']}')"
    execute_query(query)
    return jsonify({"message": "Order created"}), 201

# Route with N+1 query problem
@app.route('/orders', methods=['GET'])
def get_orders():
    query = "SELECT * FROM orders"
    orders = execute_query(query)
    
    result = []
    for order in orders:
        item_query = f"SELECT * FROM order_items WHERE order_id = {order[0]}"
        items = execute_query(item_query)
        result.append({
            "order": order,
            "items": items
        })
    
    return jsonify(result)

# Route with broken update
@app.route('/order/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    data = request.get_json()
    query = f"UPDATE orders SET status = '{data['status']}' WHERE id = {order_id}"
    execute_query(query)
    return jsonify({"message": "Order updated"})

# Route with missing authentication
@app.route('/menu', methods=['POST'])
def add_menu_item():
    data = request.get_json()
    query = f"INSERT INTO menu_items (name, description, price, category) VALUES ('{data['name']}', '{data['description']}', {data['price']}, '{data['category']}')"
    execute_query(query)
    return jsonify({"message": "Menu item added"}), 201

if __name__ == '__main__':
    app.run(debug=True)