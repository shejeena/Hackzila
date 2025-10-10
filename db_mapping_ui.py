import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage, filedialog
from dbconnector import DBConnector
from auth_config import ApiAuth
import httpx
import asyncio
import re
import os
import json
import time

class DBFormApp(tk.Frame):
    def __init__(self, parent, db_type, db_handler):
        super().__init__(parent)
        self.root = parent
        self.dbtype = db_type
        self.dbconnector = DBConnector(db_type, db_handler)

        self.method_var = tk.StringVar(value="GET")
        self.api_path_var = tk.StringVar()
        self.table_var = tk.StringVar()

        # Auth-related StringVars remain in the UI, but logic is moved to ApiAuth
        self.token_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # Create ApiAuth and pass the StringVars so it reads current UI values dynamically
        self.auth = ApiAuth(self.token_var, self.api_key_var, self.username_var, self.password_var)

        self.fields_frame = None
        self.inputs = {}
        self.error_labels = {}
        self.history_file = "request_history.json"

        icon_path = os.path.join("resources", "export.png")
        self.export_icon = PhotoImage(file=icon_path)

        self.build_ui()

    def build_ui(self):
        ttk.Label(self.root, text="HTTP Method:").pack(pady=5)
        method_dropdown = ttk.Combobox(self.root, textvariable=self.method_var,
                                       values=["GET", "POST", "PUT", "DELETE"], state="readonly")
        method_dropdown.pack(pady=5)
        method_dropdown.bind("<<ComboboxSelected>>", self.on_method_change)

        path_frame = ttk.Frame(self.root)
        path_frame.pack(pady=5, fill=tk.X)
        ttk.Label(path_frame, text="API Path:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(path_frame, textvariable=self.api_path_var, width=30).pack(side=tk.LEFT)
        ttk.Button(path_frame, text="Send", command=self.send_request).pack(side=tk.LEFT, padx=(5, 0))

        
        table_frame = ttk.Frame(self.root)
        table_frame.pack(pady=5, fill=tk.X)
        ttk.Label(table_frame, text="Select Table:").pack()
        self.table_dropdown = ttk.Combobox(table_frame, textvariable=self.table_var, state="readonly")
        self.table_dropdown.pack()
        self.table_dropdown.bind("<<ComboboxSelected>>", self.load_columns)
         # Scrollable input frame
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.fields_frame = ttk.Frame(self.canvas)  # This is your scrollable content

        self.fields_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        response_frame = ttk.Frame(self.root)
        response_frame.pack(pady=(10, 0), fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(response_frame)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Response:").pack(side=tk.LEFT, padx=5)
        self.export_btn = ttk.Button(header_frame, image=self.export_icon, command=self.export_response, state="disabled")
        self.export_btn.pack(side=tk.RIGHT, padx=5)

        response_scroll = ttk.Scrollbar(response_frame)
        response_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.response_text = tk.Text(response_frame, height=10, width=50, yscrollcommand=response_scroll.set)
        self.response_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.response_text.config(state=tk.DISABLED)
        response_scroll.config(command=self.response_text.yview)

        self.load_tables()

    def set_connection(self, conn):
        self.dbconnector = DBConnector(self.dbtype, conn)
        self.load_tables()

    def load_tables(self):
        if not self.dbconnector.get_connection():
            self.table_dropdown['values'] = []
            return
        try:
            tables = self.dbconnector.get_table_names()
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to load tables:\n{e}")
            tables = []
        self.table_dropdown['values'] = tables
        if tables:
            self.table_var.set(tables[0])
            self.load_columns()

    def on_method_change(self, event=None):
        if self.table_var.get():
            self.load_columns()

    def load_columns(self, event=None):
        table = self.table_var.get()
        method = self.method_var.get()
        if not self.dbconnector.get_connection():
            return
        try:
            columns = self.dbconnector.get_table_columns(table) or []
        except Exception as e:
            messagebox.showerror("DB Error", f"Failed to load columns for {table}:\n{e}")
            columns = []

        if method in ["POST", "PUT"]:
            audit_keywords = ['created', 'updated', 'modified', 'timestamp', 'status', 'deleted']
            columns = [(name, dtype) for name, dtype in columns
                       if not any(keyword in (name or "").lower() for keyword in audit_keywords)]

        # Clear previous field frame from canvas
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        self.fields_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")


        self.inputs = {}
        self.error_labels = {}

        for col_name, col_type in columns:
            ttk.Label(self.fields_frame, text=f"{col_name} ({col_type})").pack()
            entry = ttk.Entry(self.fields_frame)
            entry.pack()
            self.inputs[col_name] = entry
            error_label = ttk.Label(self.fields_frame, text="", foreground="red")
            error_label.pack()
            self.error_labels[col_name] = error_label
        
        # Ensure canvas scrollregion updates
        self.fields_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def validate_inputs(self):
        errors = []
        table = self.table_var.get()
        for label in self.error_labels.values():
            label.config(text="")
        try:
            columns = self.dbconnector.get_table_columns(table)
        except:
            return ["Unable to fetch column types for validation."]
        for col_name, entry in self.inputs.items():
            value = entry.get().strip()
            if not value:
                continue
            col_type = next((dtype for name, dtype in columns if name == col_name), None)
            if not col_type:
                continue
            error_msg = ""
            if "int" in col_type.lower() and not value.isdigit():
                error_msg = f"{col_name} must be an integer."
            elif "float" in col_type.lower() or "double" in col_type.lower():
                try:
                    float(value)
                except ValueError:
                    error_msg = f"{col_name} must be a float."
            elif "date" in col_type.lower():
                if not re.match(r"\d{4}-\d{2}-\d{2}", value):
                    error_msg = f"{col_name} must be YYYY-MM-DD."
            if error_msg:
                self.error_labels[col_name].config(text=error_msg)
                errors.append(error_msg)
        return errors

    # Delegate to ApiAuth instance
    def build_auth_headers(self):
        return self.auth.build_headers()

    def build_basic_auth(self):
        return self.auth.build_basic_auth()

    def send_request(self):
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.config(state=tk.DISABLED)
        self.export_btn.config(state="disabled")
        if self.validate_inputs():
            return
        asyncio.run(self._perform_request())

    async def _perform_request(self):
        method = self.method_var.get()
        url = self.api_path_var.get().strip()
        payload = {col: entry.get() for col, entry in self.inputs.items()}
        params = {col: entry.get().strip() for col, entry in self.inputs.items() if entry.get().strip()}
        headers = self.build_auth_headers()
        auth = self.build_basic_auth()

        try:
            async with httpx.AsyncClient() as client:
                t0 = time.perf_counter()
                if method == "GET":
                    if not params:
                        self._update_response("Error: At least one search parameter is required.\n")
                        return
                    response = await client.get(url, params=params, headers=headers, auth=auth, timeout=10)
                elif method == "POST":
                    response = await client.post(url, json=payload, headers=headers, auth=auth, timeout=10)
                elif method == "PUT":
                    response = await client.put(url, json=payload, headers=headers, auth=auth, timeout=10)
                elif method == "DELETE":
                    response = await client.delete(url, params=params, headers=headers, auth=auth, timeout=10)
                else:
                    raise ValueError("Unsupported method")
                t1 = time.perf_counter()

                try:
                    parsed = response.json()
                    formatted = json.dumps(parsed, indent=2)
                    result = formatted
                except:
                    result = response.text[:1000] + "\n\n[Truncated]" if len(response.text) > 1000 else response.text
                t2 = time.perf_counter()

                duration_ms = round((t1 - t0) * 1000, 2)
                parse_ms = round((t2 - t1) * 1000, 2)

                self._update_response(f"Status: {response.status_code}\nTime: {duration_ms} ms\nParse: {parse_ms} ms\n\n{result}")
                self.response_text.after(0, lambda: self.export_btn.config(state="normal"))
                self.save_history(method, url, payload, result)

        except Exception as e:
            self._update_response(f"Error: {str(e)}")

    def _update_response(self, text):
        def update():
            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert(tk.END, text)
            self.response_text.config(state=tk.DISABLED)
        self.response_text.after(0, update)

    def export_response(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Response As"
        )

        if file_path:
            try:
                content = self.response_text.get("1.0", tk.END).strip()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Export Successful", f"Response saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not save file:\n{e}")

    def save_history(self, method, url, payload, response_text):
        entry = {
            "method": method,
            "url": url,
            "payload": payload,
            "response": response_text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            else:
                history = []

            history.append(entry)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history[-50:], f, indent=2)  # Keep last 50 entries
        except Exception as e:
            print(f"History save failed: {e}")

    def generate_curl_command(self, method, url, payload):
        try:
            headers = " -H 'Content-Type: application/json'"
            data = f" -d '{json.dumps(payload)}'" if payload else ""
            return f"curl -X {method} '{url}'{headers}{data}"
        except Exception as e:
            return f"Error generating cURL: {e}"

