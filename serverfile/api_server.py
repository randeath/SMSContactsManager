from flask import Flask, request, jsonify
import config
import db
from gevent.pywsgi import WSGIServer
import socket


class ReusableWSGIServer(WSGIServer):
    def init_socket(self):
        super().init_socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


app = Flask(__name__)

config_data = config.load_config()
mydb = db.connect_to_db(config_data)
mycursor = mydb.cursor()

db.create_messages_table(mycursor)
app_user = config.get_app_user(config_data)

@app.route('/send_sms', methods=['POST'])
def send_sms():
    phone_number = request.json['phone_number']
    message = request.json['message']

    query = "INSERT INTO messages (phone_number, message, user) VALUES (%s, %s, %s)"
    mycursor.execute(query, (phone_number, message, app_user))
    mydb.commit()

    return jsonify({"status": "success", "message": f"Message is ready to be sent to {phone_number}"})


@app.route('/get_messages', methods=['GET'])
def get_messages():
    query = "SELECT * FROM messages WHERE user = %s"
    mycursor.execute(query, (app_user,))
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

def start_server():
    server = app.run(debug=True, host='0.0.0.0', port=8000)
    return server


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8000

    server = ReusableWSGIServer((host, port), app)
    server.serve_forever()
