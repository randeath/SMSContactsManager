from flask import Flask, request, jsonify
import mariadb
import json

app = Flask(__name__)

# Load configuration from the JSON file
with open('config.json') as f:
    config = json.load(f)

# Connect to the MariaDB database
def get_connection():
    return mariadb.connect(**config)

# API endpoint to delete data from the database
@app.route('/delete_data', methods=['POST'])
def delete_data():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get the 'id' parameter from the request
        message_id = request.form.get('id')

        # Delete the data with the given 'id' from the database
        cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()

        # Close the database connection
        conn.close()

        # Return a JSON response indicating success
        return jsonify({'status': 'success'})

    except mariadb.Error as e:
        print(f"Error deleting data: {e}")
        return jsonify({'status': 'error'})

# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
