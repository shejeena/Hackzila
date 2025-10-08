import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from dbconnector import DBConnector
import dbconnector

class DBFormApp(tk.Frame):
    def __init__(self, parent, db_type, db_handler):
        super().__init__(parent)
        self.root = parent
        self.db = db_handler
        self.root.title("Dynamic DB Form")
        self.table_var = tk.StringVar()
        self.fields_frame = None
        self.dbtype = db_type
        self.dbconnector = DBConnector(db_type, db_handler)
        self.build_ui()

    def build_ui(self):
        ttk.Label(self.root, text="Select Table:").pack(pady=5)
        self.table_dropdown = ttk.Combobox(self.root, textvariable=self.table_var, state="readonly")
        self.table_dropdown.pack(pady=5)
        self.table_dropdown.bind("<<ComboboxSelected>>", self.load_columns)

        self.load_tables()

    def load_tables(self):
        tables = self.dbconnector.get_table_names()
        self.table_dropdown['values'] = tables

    def load_columns(self, event=None):
        table = self.table_var.get()
        columns = self.dbconnector.get_table_columns(table)

        if self.fields_frame:
            try:
                self.fields_frame.pack_forget()
            except Exception:
                self.fields_frame.destroy()

        self.fields_frame = ttk.Frame(self.root)
        self.fields_frame.pack(pady=10)

        self.inputs = {}
        for col_name, col_type in columns:
            ttk.Label(self.fields_frame, text=col_name).pack()
            entry = ttk.Entry(self.fields_frame)
            entry.pack()
            self.inputs[col_name] = entry

        ttk.Button(self.fields_frame, text="Submit", command=self.submit_form).pack(pady=10)

    def submit_form(self):
        data = {col: entry.get() for col, entry in self.inputs.items()}
        messagebox.showinfo("Form Submitted", f"Payload:\n{data}")
