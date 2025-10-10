import pytest
import tkinter as tk
import tkinter.messagebox as messagebox
from auth_config import ApiAuth, AuthConfigUI

@pytest.fixture(scope="module")
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

def test__get_with_stringvar(tk_root):
    sv = tk.StringVar(tk_root, value="  token  ")
    api = ApiAuth(token_var=sv)
    assert api._get(sv) == "token"

def test__get_with_none_returns_empty():
    api = ApiAuth()
    assert api._get(None) == ""

def test__get_with_plain_value():
    api = ApiAuth()
    assert api._get("  plain  ") == "plain"

def test_build_headers_and_basic_auth_with_stringvars(tk_root):
    token_var = tk.StringVar(tk_root, value="tok")
    api_key_var = tk.StringVar(tk_root, value="key")
    username_var = tk.StringVar(tk_root, value="user")
    password_var = tk.StringVar(tk_root, value="pass")
    api = ApiAuth(token_var=token_var, api_key_var=api_key_var,
                  username_var=username_var, password_var=password_var)

    headers = api.build_headers()
    assert headers["Authorization"] == "Bearer tok"
    assert headers["x-api-key"] == "key"

    assert api.build_basic_auth() == ("user", "pass")

    expected = {"token": "tok", "api_key": "key", "username": "user", "password": "pass"}
    assert api.as_dict() == expected

def test_build_headers_with_plain_strings():
    api = ApiAuth(token_var="plain-token", api_key_var=None)
    assert api.build_headers() == {"Authorization": "Bearer plain-token"}

def test_authconfigui_preview_auth_calls_messagebox(monkeypatch, tk_root):
    ui = AuthConfigUI(tk_root)
    # Set values in the UI stringvars
    ui.token_var.set("t1")
    ui.api_key_var.set("k1")
    ui.username_var.set("u1")
    ui.password_var.set("p1")

    captured = {}
    def fake_showinfo(title, msg):
        captured["title"] = title
        captured["msg"] = msg

    monkeypatch.setattr(messagebox, "showinfo", fake_showinfo)
    ui.preview_auth()

    assert captured.get("title") == "Auth Preview"
    # as_dict() is formatted into the message string; check substrings
    assert "'token': 't1'" in captured.get("msg", "")
    assert "'api_key': 'k1'" in captured.get("msg", "")
    assert "'username': 'u1'" in captured.get("msg", "")
    assert "'password': 'p1'" in captured.get("msg", "")