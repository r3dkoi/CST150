from flask import Flask, request, jsonify
import os, logging, pymysql #Added logging and pymysql for the try-catch blocks
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB #Added to fix Connection pooling issue
from flask_httpauth import HTTPBasicAuth #Added for authorisation fix

load_dotenv()

app = Flask(__name__)
#flaskext.mysql's MySQL()/init_app(app) removed: pool below is now the sole connection source

#For authorisation
auth = HTTPBasicAuth() #Reads/chercks authorisation header, and auto-returns 401 if it fails

@auth.verify_password
def verify_password(username, password): 
    """ Upon successful return of username, access to route is granted. 
    Returning none is access denial. """
    if username == os.getenv('API_USER') and password == os.getenv('API_PASS'):
        return username

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
    """ Runs a parameterised query using a pooled connection, commits writes,
    and returns either the new row's id (return_id=True) or the fetched rows. """
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
    """ Returns a single menu item by id, or a 404 if no matching item exists. """
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


#Missing features fix: builds the WHERE/ORDER BY clauses and params for filtering by category
#and sorting by price, kept separate from get_menu for decluttering
def build_menu_query(args):
    """ Builds the WHERE/ORDER BY clauses and params for filtering/sorting menu items. """
    query = "SELECT * FROM menu_items"
    params = []

    category = args.get('category')
    if category:
        query += " WHERE category = %s"
        params.append(category)

    if args.get('sort') == 'price':
        query += " ORDER BY price"

    return query, params

# Route with missing error handling
@app.route('/menu', methods=['GET'])
def get_menu():
    """ Returns a page of menu items, optionally filtered by ?category= and sorted with ?sort=price."""
    #Added a try-catch block and pagination fixes
    try:
        try:
            page = int(request.args.get('page', 1)) #Defaults to page 1 if not provided
            limit = int(request.args.get('limit', 5)) #Defaults to 5 items per page
        except ValueError:
            return jsonify({"error": "page and limit must be valid numbers"}), 400
        offset = (page - 1) * limit

        #Missing features fix: filtering by category and sorting by price
        query, params = build_menu_query(request.args)
        query += " LIMIT %s OFFSET %s"
        params += [limit, offset]

        items = execute_query(query, tuple(params))
        return jsonify(items)
    except pymysql.err.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to get menu"}), 500

# Route with broken POST implementation
@app.route('/order', methods=['POST'])
@auth.login_required #Auth fix: writes to the database, so requires Basic Auth credentials
def create_order():
    """ Creates a new order from a customer_name, requires auth, and returns the new order's id. """
    #Added a try-catch block
    try:
        data = request.get_json()
        if not data:
                    return jsonify({"error": "Request body must be valid JSON"}), 400 #HTTP Status fix added
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
    """ Returns a page of orders with their items grouped together, using ?page= and ?limit= query params. """
    #Added a try-catch block
    try:
        try:
            page = int(request.args.get('page', 1)) #Defaults to page 1 if not provided
            limit = int(request.args.get('limit', 5)) #Defaults to 5 orders per page
        except ValueError:
            return jsonify({"error": "page and limit must be valid numbers"}), 400
        offset = (page - 1) * limit

        #Pagination fix: paginate on orders first (one row per order), so a page always
        #contains whole orders instead of cutting an order's items off mid-way
        orders_query = "SELECT * FROM orders LIMIT %s OFFSET %s"
        orders_rows = execute_query(orders_query, (limit, offset))

        order_ids = [row[0] for row in orders_rows] #row[0] is order_id

        #No orders on this page (e.g. page number beyond the last page) - nothing to join, return empty
        if not order_ids:
            return jsonify([])

        #Builds one %s placeholder per order_id, since IN (...) needs one per value
        placeholders = ', '.join(['%s'] * len(order_ids))
        items_query = f"SELECT order_id, item_id, quantity, subtotal FROM order_details WHERE order_id IN ({placeholders})"
        item_rows = execute_query(items_query, tuple(order_ids))

        #Groups items by order_id so they can be attached to the right order below
        items_by_order = {}
        for order_id, item_id, quantity, subtotal in item_rows:
            items_by_order.setdefault(order_id, []).append((item_id, quantity, subtotal))

        result = []
        for row in orders_rows:
            order_id = row[0]
            result.append({
                "order": row,
                "items": items_by_order.get(order_id, []) #Empty list if this order has no items
            })

        return jsonify(result)
    except pymysql.err.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to get orders"}), 500

# Route with broken update
@app.route('/order/<int:order_id>', methods=['PUT'])
@auth.login_required #Auth fix: writes to the database, so requires Basic Auth credentials
def update_order(order_id):
    """ Updates an existing order's status, requires auth, and 404s if the order_id doesn't exist. """
    #Added try-catch block
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400 #HTTP Status fix added
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

#Example of Delete Endpoint Created
@app.route('/menu/<int:item_id>', methods=['DELETE'])
@auth.login_required
def delete_menu_item():
    """Removes an existing menu item from the menu"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400 
        check_query = "SELECT * FROM menu_items WHERE item_id = %s" 
        existing_menu_item = execute_query(check_query, (item_id,))
        if not existing_menu_item: 
                return jsonify({"error": "Menu item not found."}), 404

        query = "DELETE FROM menu_items WHERE item_id = %s"
        if 'item_id' in data:
            execute_query(query, (data['item_id']),)
            return jsonify({"message": "Menu item removed."})
        else:
            return jsonify({"error": "Valid item required"}), 400
    except pymysql.err.Error as e: 
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Unable to update order"}), 500

# Route with missing authentication
@app.route('/menu', methods=['POST'])
@auth.login_required #Auth fix: writes to the database, so requires Basic Auth credentials
def add_menu_item():
    """ Adds a new menu item from name/description/price/category, requires auth. """
    #Aded try-catch block
    try:
        data = request.get_json()
        if not data:
                    return jsonify({"error": "Request body must be valid JSON"}), 400 #HTTP Status fix added
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