from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import config
import db

app = Flask(__name__)
socketio = SocketIO(app)

config_data = config.load_config()
mydb = db.connect_to_db(config_data)
mycursor = mydb.cursor()

db.create_messages_table(mycursor)
app_user = config.get_app_user(config_data)  # Remove the mycursor parameter

# ... Rest of the code with routes and functions
def notify_db_change():
    socketio.emit('db_change', {"message": "Database has been updated"})

@app.route('/send_sms', methods=['POST'])
def send_sms():
    phone_number = request.json['phone_number']
    message = request.json['message']

    query = "INSERT INTO messages (phone_number, message, user) VALUES (%s, %s, %s)"
    mycursor.execute(query, (phone_number, message, config['app_user']))
    mydb.commit()

    notify_db_change()

    return jsonify({"status": "success", "message": f"Message is ready to be sent to {phone_number}"})


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


@app.route('/delete_message', methods=['POST'])
def delete_message():
    message_id = request.json['message_id']

    query = "DELETE FROM messages WHERE id = %s"
    mycursor.execute(query, (message_id,))
    mydb.commit()

    notify_db_change()

    return jsonify({"status": "success", "message": f"Message with id {message_id} has been deleted"})


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8000)
