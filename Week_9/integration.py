from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
host="localhost",
user="root",
password="SterileDept1!",
database="webapp_db"
)
cursor = db.cursor()

@app.route("/users", methods=["GET"])
def get_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify(users)

if __name__ == "__main__":
    app.run(debug=True)