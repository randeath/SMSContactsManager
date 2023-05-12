from flask import Flask, request, jsonify, abort
import mysql.connector
import json
import time
import os

app = Flask(__name__)
##
# Get the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the path to the config.json file relative to the script directory
config_file_path = os.path.join(script_dir, '..', 'config.json')

# Load the configuration from the config.json file
with open(config_file_path) as f:
    config = json.load(f)

# Check if 'recent_app_user' exists in the config file, otherwise prompt for user input
if 'recent_app_user' in config:
    user_id = config['recent_app_user']
else:
    user_id = input("Please enter an ID: ")
    config["recent_app_user"] = user_id
    # Save the updated config dictionary to the config.json file
    with open('config.json', 'w') as f:
        json.dump(config, f)

config["user_id"] = user_id

mydb = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)
mycursor = mydb.cursor()
mycursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    phone_number VARCHAR(255),
                    message TEXT,
                    user_id VARCHAR(255)
                )""")

@app.route('/')
def hello():
    return "SMS System is working"

def check_stop_file():
    # Set the path to the stop_server.txt file relative to the script directory
    stop_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stop_server.txt')

    return os.path.exists(stop_file_path)

def remove_stop_file():
    stop_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stop_server.txt')
    
    if os.path.exists(stop_file_path):
        os.remove(stop_file_path)



@app.route('/send_sms', methods=['POST'])
def send_sms():
    phone_number = request.json['phone_number']
    message = request.json['message']

    query = "INSERT INTO messages (phone_number, message, user_id) VALUES (%s, %s, %s)"
    mycursor.execute(query, (phone_number, message, config['user_id']))
    mydb.commit()

    return jsonify({"status": "success", "message": f"Message is ready to be sent to {phone_number}"})

@app.route('/delete_message/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    # Check if the message with the given ID exists
    mycursor.execute("SELECT COUNT(*) FROM messages WHERE id = %s", (message_id,))
    count = mycursor.fetchone()[0]

    if count == 0:
        # Message with the given ID does not exist, return a 404 error
        abort(404)
    else:
        # Delete the message with the given ID
        mycursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
        mydb.commit()

    return jsonify({"status": "success", "message": f"Message with ID {message_id} has been deleted"})



@app.route('/get_messages', methods=['GET'])
def get_messages():
    mycursor.execute("SELECT * FROM messages")
    result = mycursor.fetchall()
    messages = []

    for row in result:
        message_data = {
            "id": row[0],
            "phone_number": row[1],
            "message": row[2],
            "user": row[3]
        }
        messages.append(message_data)

    return jsonify({"status": "success", "messages": messages})

def create_server_instance():
    return app


if __name__ == '__main__':
    while True:
        if check_stop_file():
            remove_stop_file()
            break
        else:
            app.run(host='0.0.0.0',port=8000)
            time.sleep(5)
