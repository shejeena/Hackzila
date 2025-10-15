import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from api_test_ui import ApiTestFrame
from dbconnector import DBConnector
from db_mapping_ui import DBFormApp
from auth_config import AuthConfigUI
import psycopg2

class HackzillaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unified UI")
        self.root.geometry("1200x600")

        self.connection = None
        self.db_connector = None

        # Create Notebook for tabbed layout
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # --- Tab 1: DB Connection ---
        self.db_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.db_tab, text="DB Connection")
        self.build_db_panel(self.db_tab)

        # --- Tab 2: API Key & Params ---
        self.api_key_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.api_key_tab, text="API Key & Params")
        self.auth_ui = AuthConfigUI(self.api_key_tab)
        self.auth_ui.frame.pack(fill="x", padx=10, pady=10)

        # --- Tab 3: Raw API Tester ---
        self.api_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.api_tab, text="Raw API Tester")
        self.api_frame = ApiTestFrame(self.api_tab)
        self.api_frame.pack(fill="both", expand=True)

    def build_db_panel(self, parent):
        tk.Label(parent, text="Database Type:").pack(pady=5)
        self.db_type_var = tk.StringVar()
        db_type_dropdown = ttk.Combobox(parent, textvariable=self.db_type_var, state="readonly")
        db_type_dropdown['values'] = ("MySQL", "PostgreSQL", "SQLite", "SQL Server", "Oracle")
        db_type_dropdown.current(1)
        db_type_dropdown.pack(pady=(0, 10))
        db_type_dropdown.bind("<<ComboboxSelected>>", self.on_db_select)

        self.host_entry = self.create_labeled_entry(parent, "Host:")
        self.port_entry = self.create_labeled_entry(parent, "Port:")
        self.user_entry = self.create_labeled_entry(parent, "Username:")
        self.password_entry = self.create_password_entry(parent)
        self.db_name_entry = self.create_labeled_entry(parent, "DB Name:")

        tk.Button(parent, text="Connect", command=self.connect_to_db).pack(pady=10)

    def create_labeled_entry(self, parent, label_text):
        frame = tk.Frame(parent)
        tk.Label(frame, text=label_text, width=12, anchor='w').pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=25)
        entry.pack(side=tk.LEFT)
        frame.pack(pady=3)
        return entry

    def create_password_entry(self, parent):
        pwd_frame = tk.Frame(parent)
        tk.Label(pwd_frame, text="Password:", width=12, anchor='w').pack(side=tk.LEFT)
        entry = tk.Entry(pwd_frame, width=21, show='*')
        entry.pack(side=tk.LEFT)

        try:
            eye_open_img = PhotoImage(file='resources\\eye_open.png')
            eye_closed_img = PhotoImage(file='resources\\eye_closed.png')
        except Exception:
            eye_open_img = PhotoImage(width=1, height=1)
            eye_closed_img = PhotoImage(width=1, height=1)

        def toggle_password():
            if entry.cget('show') == '':
                entry.config(show='*')
                eye_button.config(image=eye_closed_img)
            else:
                entry.config(show='')
                eye_button.config(image=eye_open_img)

        eye_button = tk.Button(pwd_frame, image=eye_closed_img, command=toggle_password, bd=0)
        eye_button.pack(side=tk.LEFT, padx=(0, 5))
        pwd_frame.pack(pady=3)
        return entry

    def on_db_select(self, event=None):
        selected_db = self.db_type_var.get()
        try:
            self.db_connector = DBConnector(selected_db)
        except Exception:
            self.db_connector = None

    def connect_to_db(self):
        db_type = self.db_type_var.get()
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.password_entry.get()
        dbname = self.db_name_entry.get().strip()

        try:
            conn = psycopg2.connect(
                dbname=dbname or "patientdb",
                user=user or "admin",
                password=password or "yourpassword",
                host=host,
                port=port
            )
            self.connection = conn
            messagebox.showinfo("Success", "Connected to the database!")
            self.load_db_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed:\n{e}")

    def load_db_ui(self):
        # Clear Tab 1 (DB Connection tab)
        for widget in self.db_tab.winfo_children():
            widget.destroy()

        # Load DBFormApp into Tab 1
        self.db_ui_frame = DBFormApp(self.db_tab, self.db_type_var.get(), self.connection, auth=self.auth_ui.auth)
        self.db_ui_frame.pack(fill="both", expand=True, padx=10, pady=10)

# --- Launch ---
if __name__ == "__main__":
    root = tk.Tk()
    app = HackzillaApp(root)
    root.mainloop()
