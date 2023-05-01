import os
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import pandas as pd
import subprocess
import csv
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector


# Your original code (up to the point where you read the CSV file)
sys.stdin.reconfigure(encoding='utf-8')

# Connect to the MySQL database
mydb = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)
mycursor = mydb.cursor()

# Create a table for storing phone numbers and messages, if it doesn't exist
mycursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        phone_number VARCHAR(255),
                        message TEXT
                    )""")

# Clear the contents of the CSV file
open('contacts.csv', 'w').close()

# Connect to the Android device
ADB_HOST = '192.168.0.12'
ADB_PORT = 5555
with open('/Users/randeath/documents/python/adbkey') as f:
    priv = f.read()
signer = PythonRSASigner('', priv)
device = AdbDeviceTcp(ADB_HOST, ADB_PORT)
device.connect(rsa_keys=[signer])

# Run the adb shell command and get the output
cmd = ['adb', 'shell', 'content', 'query', '--uri', 'content://contacts/phones', '--projection', 'display_name:number']
output = subprocess.check_output(cmd)

# Decode the binary output to a string
output_str = output.decode('utf-8')

# Split the string into lines and remove any trailing newline characters
lines = [line.strip() for line in output_str.split('\n')]

# Create a list of dictionaries, where each dictionary represents a row in the output
rows = []
for line in lines:
    if line:
        name, number = line.split(',')
        name = name.split('=', 1)[-1].strip()
        number = number.split('=', 1)[-1].strip()
        rows.append({'display_name': name, 'number': number})

# Save the list of dictionaries to a CSV file
with open('contacts.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['display_name', 'number'])
    writer.writeheader()
    writer.writerows(rows)

# Read the CSV file and display the contacts
contacts_df = pd.read_csv('contacts.csv')

# Create a Tkinter window for the GUI
root = tk.Tk()
root.title("Contact Messaging")

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

def send_sms():
    # Get the phone number from the entry box
    phone_number = entry_phone_number.get()

    # Get the message from the entry box
    message = entry_message.get()

    # Insert the data into the MySQL database
    cursor = mydb.cursor()
    query = "INSERT INTO sent_messages (phone_number, message) VALUES (%s, %s)"
    cursor.execute(query, (phone_number, message))
    mydb.commit()

    # Show a confirmation message
    messagebox.showinfo("SMS Ready", f"Message is ready to be sent to {phone_number}")

    # You can now use the selected phone number and message for further processing.
    print("Selected phone number:", phone_number)
    print("Message to be sent:", message)

# tk img_section
# Create and populate the listbox with contact names
intro_listbox = "원하는 사람을 누르고 선택을 눌러주세요"
intro_label = tk.Label(root, text=intro_listbox)
intro_label.pack(pady=10)

listbox_contacts = tk.Listbox(root,width=50, height=20)
for index, row in contacts_df.iterrows():
    listbox_contacts.insert(index, f"{row['display_name']} ({row['number']})")
listbox_contacts.pack(pady=1)

# Create a button to add the selected contact's phone number to the entry box
button_add = tk.Button(root, text="선택", command=add_selected_contact)
button_add.pack(pady=3)

intro_listbox2 = "원하는 사람 입력하고 찾기를 눌러주세요"
intro_label2 = tk.Label(root, text=intro_listbox, justify='center')
intro_label2.pack(pady=10)

# Create an entry box for the display_name input
entry_display_name = tk.Entry(root, width=50)
entry_display_name.pack(pady=10)

# Create a button to proceed with the entered contact name or phone number
button_proceed = tk.Button(root, text="찾기", command=process_contact)
button_proceed.pack(pady=10)

# Create an entry box for the phone number input (optional)
entry_phone_number = tk.Entry(root,width=50)
entry_phone_number.pack(pady=10)

intro_listbox3 = "번호"
intro_label3 = tk.Label(root, text=intro_listbox)
intro_label3.pack(pady=10)

# Create an entry box for the message
entry_message = tk.Entry(root, width=50)
entry_message.pack(pady=10)

# Create a button to send the SMS
button_send = tk.Button(root, text="Send SMS", command=send_sms)
button_send.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()

# Close the connection
device.close()