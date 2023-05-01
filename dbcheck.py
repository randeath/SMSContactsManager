import mysql.connector
import json

# Load the configuration from the config.json file
with open('config.json') as f:
    config = json.load(f)

# Connect to the MySQL database using the credentials from the config.json file
mydb = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)

# Create a cursor
mycursor = mydb.cursor()

# Execute a SELECT query
mycursor.execute("SELECT * FROM messages")

# Fetch all rows from the result
result = mycursor.fetchall()

# Display the result
for row in result:
    print(row)

# Close the cursor and connection
mycursor.close()
mydb.close()
