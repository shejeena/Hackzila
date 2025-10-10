# auth_config.py
import tkinter as tk
from tkinter import ttk, messagebox

class ApiAuth:
    def __init__(self, token_var=None, api_key_var=None, username_var=None, password_var=None):
        self.token_var = token_var
        self.api_key_var = api_key_var
        self.username_var = username_var
        self.password_var = password_var    

    def _get(self, v):
        if v is None:
            return ""
        try:
            return v.get().strip()
        except Exception:
            return str(v).strip()

    def build_headers(self):
        headers = {}
        token = self._get(self.token_var)
        api_key = self._get(self.api_key_var)
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if api_key:
            headers["x-api-key"] = api_key
        return headers

    def build_basic_auth(self):
        user = self._get(self.username_var)
        pwd = self._get(self.password_var)
        return (user, pwd) if user and pwd else None

    def as_dict(self):
        return {
            "token": self._get(self.token_var),
            "api_key": self._get(self.api_key_var),
            "username": self._get(self.username_var),
            "password": self._get(self.password_var),
        }

class AuthConfigUI:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=10)

        self.token_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.auth = ApiAuth(
            token_var=self.token_var,
            api_key_var=self.api_key_var,
            username_var=self.username_var,
            password_var=self.password_var
        )

        self.build_ui()

    def build_ui(self):
        tk.Label(self.frame, text="Bearer Token:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.frame, textvariable=self.token_var, width=40).grid(row=0, column=1, sticky="w", padx=10, pady=5)

        tk.Label(self.frame, text="API Key:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.frame, textvariable=self.api_key_var, width=40).grid(row=1, column=1, sticky="w", padx=10, pady=5)

        tk.Label(self.frame, text="Username:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.frame, textvariable=self.username_var, width=40).grid(row=2, column=1, sticky="w", padx=10, pady=5)

        tk.Label(self.frame, text="Password:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.frame, textvariable=self.password_var, show="*", width=40).grid(row=3, column=1, sticky="w", padx=10, pady=5)

        tk.Button(self.frame, text="Preview Auth", command=self.preview_auth).grid(row=4, column=1, sticky="w", padx=10, pady=10)

    def preview_auth(self):
        messagebox.showinfo("Auth Preview", f"{self.auth.as_dict()}")
