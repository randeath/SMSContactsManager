import os
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import pandas as pd
import subprocess
import csv
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

# Your original code (up to the point where you read the CSV file)
sys.stdin.reconfigure(encoding='utf-8')

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
print(contacts_df)
# Read the CSV file and display the contacts
contacts_df = pd.read_csv('contacts.csv')

# Create a Tkinter window for the GUI
root = tk.Tk()
root.title("Contact Messaging")

# Function to send an SMS
def send_sms():
    # Get the selected contact index from the listbox
    selected_contact_index = listbox_contacts.curselection()[0]

    # Get the selected contact's name and phone number
    selected_contact_name = contacts_df.loc[selected_contact_index, 'display_name']
    phone_number = contacts_df.loc[selected_contact_index, 'number']

    # Get the message from the entry box
    message = entry_message.get()

    # You can now use the selected phone number and message for further processing.
    print("Selected phone number:", phone_number)
    print("Message to be sent:", message)

    # Show a confirmation message
    messagebox.showinfo("SMS Sent", f"Message sent to {selected_contact_name}")

# Create and populate the listbox with contact names
listbox_contacts = tk.Listbox(root)
for index, row in contacts_df.iterrows():
    listbox_contacts.insert(index, f"{row['display_name']} ({row['number']})")
listbox_contacts.pack(pady=10)

# Create an entry box for the message
entry_message = tk.Entry(root)
entry_message.pack(pady=10)

# Create a button to send the SMS
button_send = tk.Button(root, text="Send SMS", command=send_sms)
button_send.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()

# Close the connection
device.close()
