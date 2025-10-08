# Hackzilla.py
from pickle import FRAME
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from api_test_ui import ApiTestFrame
from dbconnector import DBConnector
from db_mapping_ui import DBFormApp
import psycopg2

# Main window
root = tk.Tk()
root.title("Unified UI")
root.geometry("400x500")

# --- Frame 1: Database Connection ---
db_frame = tk.Frame(root)
db_frame.pack(fill="both", expand=True)

tk.Label(db_frame, text="Database Type:").pack(pady=5)
db_type_var = tk.StringVar()
db_type_dropdown = ttk.Combobox(db_frame, textvariable=db_type_var, state="readonly")
db_type_dropdown['values'] = ("MySQL", "PostgreSQL", "SQLite", "SQL Server", "Oracle")
db_type_dropdown.current(1)  # default to PostgreSQL

# Bind selection changes on the Combobox to a local handler
db_connector = None  # will hold DBConnector instance if needed

connection = None

def set_dbconnection(conn):
    global connection
    connection = conn

def on_db_select(event=None):
    """
    Called when the combobox selection changes.
    Recreate or update the DBConnector for the selected database type.
    """
    global db_connector
    selected_db = db_type_var.get()
    try:
        db_connector = DBConnector(selected_db)
    except Exception:
        db_connector = None  # fail gracefully if DBConnector not available


# Pack the combobox and bind the event
db_type_dropdown.pack(pady=(0, 10))
db_type_dropdown.bind("<<ComboboxSelected>>", on_db_select)

def create_labeled_entry(parent, label_text, show=None):                            
    frame = tk.Frame(parent)
    tk.Label(frame, text=label_text, width=12, anchor='w').pack(side=tk.LEFT)
    entry = tk.Entry(frame, width=25)
    if show:
        entry.config(show=show)
    entry.pack(side=tk.LEFT)
    frame.pack(pady=3)
    return entry

# Load eye icons (use your own .png files)
try:
    eye_open_img = PhotoImage(file='resources\\eye_open.png')
    eye_closed_img = PhotoImage(file='resources\\eye_closed.png')
except Exception:
    # Fallback: create simple empty images to avoid crashes if files missing
    eye_open_img = PhotoImage(width=1, height=1)
    eye_closed_img = PhotoImage(width=1, height=1)

host_entry = create_labeled_entry(db_frame, "Host:")
port_entry = create_labeled_entry(db_frame, "Port:")
user_entry = create_labeled_entry(db_frame, "Username:")
# Password row with eye button
pwd_frame = tk.Frame(db_frame)
password_label = tk.Label(pwd_frame, text="Password:", width=12, anchor='w').pack(side=tk.LEFT)
password_entry = tk.Entry(pwd_frame, width=21, show='*')
password_entry.pack(side=tk.LEFT)


def toggle_password():
    if password_entry.cget('show') == '':
        password_entry.config(show='*')
        eye_button.config(image=eye_closed_img)
    else:
        password_entry.config(show='')
        eye_button.config(image=eye_open_img)


eye_button = tk.Button(pwd_frame, image=eye_closed_img, command=toggle_password, bd=0)
eye_button.pack(side=tk.LEFT, padx=(0, 5))
pwd_frame.pack(pady=3)

db_name_entry = create_labeled_entry(db_frame, "DB Name:")


# --- Database connection logic ---
def connect_to_db():
    db_type = db_type_var.get()
    host = host_entry.get().strip()
    port = port_entry.get().strip()
    user = user_entry.get().strip()
    password = password_entry.get()
    dbname = db_name_entry.get().strip()

    try:
        # For now, use psycopg2 to connect to PostgreSQL parameters.
        # In a fuller implementation, switch connector based on `db_type`.
        conn = psycopg2.connect(
            dbname=dbname or "patientdb",
            user=user or "admin",
            password=password or "yourpassword",
            host=host,
            port=port
        )
        set_dbconnection(conn)
        # conn.close()
        messagebox.showinfo("Success", "Connected to the database!")
        show_api_ui()
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"Connection failed:\n{e}")
        return False

# --- Frame 2: API Test UI (imported) ---
#api_frame = ApiTestFrame(root)  # created but not packed initially
#db_frame = DBFormApp(root)

def show_api_ui():
    db_frame2 = DBFormApp(root,db_type_var.get(), connection)
    db_frame.pack_forget()
    db_frame2.pack(fill="both", expand=True)


def connect_and_show():
    if connect_to_db():
        show_api_ui()

tk.Button(db_frame, text="Connect", command=connect_to_db).pack(pady=10)

root.mainloop()
