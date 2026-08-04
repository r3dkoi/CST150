from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'SterileDept1!'
app.config['MYSQL_DB'] = 'flask_db'
mysql = MySQL(app)

@app.route('/users', methods=['GET'])
def get_users():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s",
    (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return jsonify(user)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (data['name'], data['email']))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'User added successfully'}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (data['name'], data['email'], user_id))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'User updated successfully'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s",
    (user_id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'User deleted successfully'})

if __name__ == "__main__":
    app.run(debug=True)
    