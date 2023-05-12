import mysql.connector

def create_database_connection(config):
    mydb = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )
    return mydb

def create_messages_table_if_not_exists(mycursor):
    mycursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            phone_number VARCHAR(255),
                            message TEXT,
                            user VARCHAR(255)
                        )""")

def insert_message(mydb, phone_number, message, user):
    mycursor = mydb.cursor()
    query = "INSERT INTO messages (phone_number, message, user) VALUES (%s, %s, %s)"
    mycursor.execute(query, (phone_number, message, user))
    mydb.commit()
