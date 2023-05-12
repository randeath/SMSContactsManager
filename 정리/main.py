import sys
import tkinter as tk
from config_manager import load_config, update_config
from adb_connection import get_adb_device, get_contacts
from database_manager import create_messages_table, insert_message
from gui_components import (create_listbox, create_button, create_label, create_entry,
                            show_warning)

# Load configuration from the JSON file
config = load_config('config.json')

# Get the user from the user input
user = input("Enter your MySQL username: ")

# Update the config dictionary with the new user value
config['user'] = user
update_config('config.json', config)

# Connect to the Android device
device = get_adb_device(config)

# Get the contacts from the Android device
contacts_df = get_contacts(device)

# Create a Tkinter window for the GUI
root = tk.Tk()
root.title("Contact Messaging")

# (Add your GUI components and functions here, using the imported functions from gui_components.py)

# Start the Tkinter main loop
root.mainloop()

# Close the connection
device.close()
