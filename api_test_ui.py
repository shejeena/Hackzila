import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json

class ApiTestFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Endpoint URL
        tk.Label(self, text="Endpoint URL:", font=('Segoe UI', 10)).pack(anchor='w', padx=10, pady=(10, 0))
        self.url_entry = tk.Entry(self, font=('Segoe UI', 10), width=80)
        self.url_entry.pack(padx=10, pady=5)

        # HTTP Method
        tk.Label(self, text="HTTP Method:", font=('Segoe UI', 10)).pack(anchor='w', padx=10)
        self.method_var = tk.StringVar(value="GET")
        self.method_menu = ttk.Combobox(self, textvariable=self.method_var, values=["GET", "POST","PUT","DELETE"], state="readonly", width=10)
        self.method_menu.pack(padx=10, pady=5)

        # Body Input
        tk.Label(self, text="Request Body (JSON):", font=('Segoe UI', 10)).pack(anchor='w', padx=10, pady=(10, 0))
        self.body_text = scrolledtext.ScrolledText(self, font=('Consolas', 10), wrap='word', width=85, height=10)
        self.body_text.pack(padx=10, pady=5)

        # Send Button
        send_btn = tk.Button(self, text="Send Request", command=self.send_request, font=('Segoe UI', 10))
        send_btn.pack(pady=10)

        # Response Display
        tk.Label(self, text="Response:", font=('Segoe UI', 10)).pack(anchor='w', padx=10)
        self.response_text = scrolledtext.ScrolledText(self, font=('Consolas', 10), wrap='word', width=70, height=15)
        self.response_text.pack(padx=10, pady=5)


    def send_request(self):
        url = self.url_entry.get()
        method = self.method_var.get()

        try:
            headers = {'Content-Type': 'application/json'}
            body = self.body_text.get("1.0", tk.END).strip()
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                 #response = requests.post(url)
                 # Try to parse body as JSON
                try:
                 json_body = json.loads(body)
                 response = requests.post(url, json=json_body, headers=headers)
                except json.JSONDecodeError:
                 self.response_text.delete(1.0, tk.END)
                 self.response_text.insert(tk.END, "❌ Invalid JSON format in request body.\n")
                 return
            elif method == "PUT":
                 #response = requests.post(url)
                 # Try to parse body as JSON
                try:
                 json_body = json.loads(body)
                 response = requests.put(url, json=json_body, headers=headers)
                except json.JSONDecodeError:
                 self.response_text.delete(1.0, tk.END)
                 self.response_text.insert(tk.END, "❌ Invalid JSON format in request body.\n")
                 return
            elif method == "DELETE":
                response = requests.delete(url)
                 
            else:
                self.response_text.insert(tk.END, "Unsupported method\n")
                return

            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, f"Status Code: {response.status_code}\n")
            self.response_text.insert(tk.END, f"Response Time: {response.elapsed.total_seconds()}s\n\n")
            self.response_text.insert(tk.END, response.text)

        except Exception as e:
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, f"Error: {str(e)}")


        


