import tkinter as tk
from tkinter import messagebox

def create_listbox(root, items, width=30, height=10):
    listbox = tk.Listbox(root, width=width, height=height)
    for index, item in enumerate(items):
        listbox.insert(index, item)
    return listbox

def create_button(root, text, command, pady=10):
    button = tk.Button(root, text=text, command=command)
    button.pack(pady=pady)
    return button

def create_label(root, text, pady=10):
    label = tk.Label(root, text=text)
    label.pack(pady=pady)
    return label

def create_entry(root, width=30, pady=10, text_variable=None):
    entry = tk.Entry(root, width=width, textvariable=text_variable)
    entry.pack(pady=pady)
    return entry

def show_warning(title, message):
    messagebox.showwarning(title, message)
