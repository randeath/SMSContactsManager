import mysql.connector

def connect_to_db(config):
    mydb = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )
    return mydb

def create_messages_table(mycursor):
    mycursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        phone_number VARCHAR(255),
                        message TEXT,
                        user VARCHAR(255)
                    )""")
