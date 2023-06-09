import subprocess
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import pandas as pd
from phrase_utils import load_phrases_from_csv, insert_selected_phrase, remove_selected_phrase, add_new_phrase
import time
import csv
import sys
import json
import tkinter as tk
from tkinter import messagebox
import mysql.connector
import os
import subprocess 
from terminate_port import terminate_process_on_port

# Your original code (up to the point where you read the CSV file)
sys.stdin.reconfigure(encoding='utf-8')

# Load configuration from the JSON file
with open('config.json') as f:
    config = json.load(f)

# Get the user from the user input
user = input("Enter your MySQL username: ")

# Update the config dictionary with the new user value
config['user'] = user

# Save the updated config dictionary to the config.json file
with open('config.json', 'w') as f:
    json.dump(config, f)

# Connect to the MySQL database
mydb = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)
mycursor = mydb.cursor()
# Create a table for storing phone numbers, messages, and users, if it doesn't exist
mycursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        phone_number VARCHAR(255),
                        message TEXT,
                        user VARCHAR(255)
                    )""")


# Read the private key
with open('/Users/randeath/documents/python/adbkey') as f:
    priv = f.read()

# Create a PythonRSASigner instance with the private key
signer = PythonRSASigner('', priv)

# Connect to the Android device
connected = False
ADB_HOST = '192.168.0.12'  # your phone adb host
ADB_PORT = 5555  # Network port

# Clear the contents of the CSV file
def clear_csv(): 
    open('contacts.csv', 'w').close()

# Try connecting via Wi-Fi
try:
    device = AdbDeviceTcp(ADB_HOST, ADB_PORT)
    device.connect(rsa_keys=[signer])
    print("Connected via Wi-Fi")
    connected = True
    clear_csv()
except Exception as e:
    print(f"Wi-Fi connection failed: {e}")
    print("Trying USB connection...")

# Try connecting via USB if Wi-Fi connection failed
if not connected:
    def run_adb_shell_command(command):
        cmd = ['adb', 'shell'] + command
        output = subprocess.check_output(cmd)
        return output.decode('utf-8')
    # Check if the device is connected via USB
    adb_devices_output = subprocess.check_output(['adb', 'devices']).decode('utf-8')
    if 'unauthorized' in adb_devices_output:
        print("Please check the connected device and authorize this computer.")
        clear_csv()
        exit(1)
    elif 'device' not in adb_devices_output:
        print("No device connected. Please connect your Android device via USB.")
        exit(1)


# Run the adb shell command and get the output
cmd = ['adb', 'shell', 'content', 'query', '--uri', 'content://com.android.contacts/data/phones', '--projection', 'display_name:data1']
output = subprocess.check_output(cmd)

# Decode the binary output to a string
output_str = output.decode('utf-8')

# Split the string into lines and remove any trailing newline characters
lines = [line.strip() for line in output_str.split('\n')]

# Create a list of dictionaries, where each dictionary represents a row in the output
rows = []
for line in lines:
    if ',' in line:
        name, number = line.split(',')
        name = name.split('=', 1)[-1].strip()
        number = number.split('=', 1)[-1].strip()
        number = number.replace('-', '')
        number = number.replace(' ', '')
        if number.startswith('1'):
            number = '0' + number

        rows.append({'display_name': name, 'number': number})


# Save the list of dictionaries to a CSV file
with open('contacts.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['display_name', 'number'])
    writer.writeheader()
    writer.writerows(rows)

# Read the CSV file and display the contacts
contacts_df = pd.read_csv('contacts.csv', dtype={'number': str})



# def section

def run_script_in_background(script_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_path)

    if sys.platform == 'win32': # For Windows
        CREATE_NEW_CONSOLE = 0x10
        DETACHED_PROCESS = 0x08
        subprocess.Popen(['python', script_path], creationflags=DETACHED_PROCESS | CREATE_NEW_CONSOLE)

    elif sys.platform == 'darwin' or sys.platform.startswith('linux'): # For macOS and Linux
        with open(os.devnull, 'w') as devnull:
            subprocess.Popen(['python', script_path], stdout=devnull, stderr=devnull, stdin=subprocess.PIPE)

    else:
        print("Unsupported operating system. Please run the script manually.")



def add_selected_contact():
    selected_index = listbox_contacts.curselection()[0]
    selected_contact = contacts_df.iloc[selected_index]
    phone_number = selected_contact['number']
    entry_phone_number.delete(0, tk.END)  # Clear the existing content
    entry_phone_number.insert(0, phone_number)  # Insert the phone number into the entry box

def process_contact():
    entered_display_name = entry_display_name.get()
    matching_contacts = contacts_df[contacts_df['display_name'] == entered_display_name]

    if matching_contacts.empty:
        messagebox.showwarning("No Matching Contact", "No matching contact found. Please enter the phone number.")
    else:
        phone_number = matching_contacts['number'].iloc[0]
        entry_phone_number.delete(0, tk.END)  # Clear the existing content
        entry_phone_number.insert(0, phone_number)  # Insert the phone number into the entry box

def send_sms_and_restart_server():
    phone_number = entry_phone_number.get()
    message = entry_message.get("1.0", tk.END).strip()
    
    # Create the table if it doesn't exist
    cursor = mydb.cursor()
    # Create a table for storing phone numbers, messages, and users, if it doesn't exist
    mycursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        phone_number VARCHAR(255),
                        message TEXT,
                        user VARCHAR(255)
                    )""")
    
    # Get the user from the JSON file
    user = config["user"]

    # Insert the data into the MySQL database
    query = "INSERT INTO messages (phone_number, message, user) VALUES (%s, %s, %s)"
    cursor.execute(query, (phone_number, message, user))
    mydb.commit()
    if __name__ == '__main__':
        terminate_process_on_port(8000)
    # Wait for a while (e.g., 5 seconds)
    time.sleep(5)
    # Restart the Flask server
    run_script_in_background('serverfile/api_server.py')

def update_button_send_state(*_):
    phone_number = entry_phone_number.get()
    message = entry_message.get("1.0", tk.END).strip()
    if phone_number and message:
        button_send.config(state=tk.NORMAL)
    else:
        button_send.config(state=tk.DISABLED)




def on_close():
    # This function will be called when the Tkinter window is closed.
    # Add code here to run another Python script, e.g.:
    subprocess.run(["python", "terminate_port.py"])
    root.destroy()

# Create a Tkinter window for the GUI
root = tk.Tk()
root.title("Contact Messaging")
root.geometry("1000x500")

# tk img_section
# Create and populate the listbox with contact names

# Load frequently used phrases from CSV
frequently_used_phrases = load_phrases_from_csv('frequently_used_phrases.csv')
message_var = tk.StringVar()
run_script_in_background('serverfile/api_server.py')

left_frame = tk.Frame(root)
left_frame.pack(side="left")

center_frame = tk.Frame(root)
center_frame.pack(side="left", expand=True, fill="both")

right_frame = tk.Frame(root)
right_frame.pack(side="left")

intro_listbox = "원하는 사람을 누르고 선택을 눌러주세요"
intro_label = tk.Label(left_frame, text=intro_listbox)
intro_label.pack(pady=5)

listbox_contacts = tk.Listbox(left_frame,width=30, height=10)
for index, row in contacts_df.iterrows():
    print(row['number'])  # Debug: print the phone number
    listbox_contacts.insert(index, f"{row['display_name']} ({row['number']})")

listbox_contacts.pack(pady=1)

# Create a button to add the selected contact's phone number to the entry box
button_add = tk.Button(left_frame, text="선택", command=add_selected_contact)
button_add.pack(pady=3)

intro_listbox2 = "원하는 사람 입력하고 찾기를 눌러주세요"
intro_label2 = tk.Label(left_frame, text=intro_listbox2, justify='center')
intro_label2.pack(pady=5)



# Create an entry box for the display_name input
entry_display_name = tk.Entry(left_frame, width=30)
entry_display_name.pack(pady=5)

# Create a button to proceed with the entered contact name or phone number
button_proceed = tk.Button(left_frame, text="찾기", command=process_contact)
button_proceed.pack(pady=5)

intro_listbox3 = " ↧번호 입력칸"
intro_label3 = tk.Label(center_frame, text=intro_listbox3)
intro_label3.pack(pady=5)

# Create an entry box for the phone number input (optional)
phone_number_var = tk.StringVar()
phone_number_var.trace_add("write", update_button_send_state)
entry_phone_number = tk.Entry(center_frame, width=30, textvariable=phone_number_var)
entry_phone_number.pack(pady=5)


# Create a listbox for frequently used phrases
listbox_phrases = tk.Listbox(center_frame, width=30)
for index, phrase in enumerate(frequently_used_phrases):
    listbox_phrases.insert(index, phrase)
listbox_phrases.pack(pady=5)

freq_message = tk.Entry(center_frame, width=30)
freq_message.pack(pady=5)

# Create a button to add a new phrase
button_add_phrase = tk.Button(center_frame, text="구문추가", command=lambda: add_new_phrase(freq_message, listbox_phrases, frequently_used_phrases, 'frequently_used_phrases.csv'))
button_add_phrase.pack(pady=5)

# Create a button to remove the selected phrase
button_remove_phrase = tk.Button(center_frame, text="저정된 구문 제거", command=lambda: remove_selected_phrase(listbox_phrases, frequently_used_phrases, 'frequently_used_phrases.csv'))
button_remove_phrase.pack(pady=5)

# Create a button to insert the selected phrase
button_insert = tk.Button(center_frame, text="구문삽입", command=lambda: insert_selected_phrase(entry_message, listbox_phrases))
button_insert.pack(pady=5)


# Create an text box for the message

entry_message = tk.Text(right_frame, width=30, height=30)
entry_message.bind("<KeyRelease>", update_button_send_state)
entry_message.pack(pady=5)

# Create a button to send the SMS
button_send = tk.Button(right_frame, text="Send SMS", command=send_sms_and_restart_server, width=20, height=2, state=tk.DISABLED)
button_send.pack(pady=5)



root.protocol("WM_DELETE_WINDOW", on_close)
# Start the Tkinter main loop
root.mainloop()

# Close the connection
device.close()