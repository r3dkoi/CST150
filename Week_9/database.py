import mysql.connector
# Connect to the MySQL database
conn = mysql.connector.connect(
host="localhost",
user="root",
password="SterileDept1!",
database="webapp_db"
)
cursor = conn.cursor()

# Retrieve data
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

# Display results
for user in users:
    print(user)

# Close connection
conn.close()