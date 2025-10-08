import pytest
import tkinter as tk
from unittest.mock import patch, Mock
from api_test_ui import ApiTestFrame

@pytest.fixture
def api_frame():
    root = tk.Tk()
    frame = ApiTestFrame(root)
    yield frame
    root.destroy()

def test_send_get_request_success(api_frame):
    api_frame.url_entry.insert(0, "http://test.com")
    api_frame.method_var.set("GET")
    mock_response = Mock(status_code=200, text="OK", elapsed=Mock(total_seconds=lambda: 0.1))
    with patch("requests.get", return_value=mock_response):
        api_frame.send_request()
    assert "Status Code: 200" in api_frame.response_text.get("1.0", tk.END)
    assert "OK" in api_frame.response_text.get("1.0", tk.END)

def test_send_post_request_with_valid_json(api_frame):
    api_frame.url_entry.insert(0, "http://test.com")
    api_frame.method_var.set("POST")
    api_frame.body_text.insert("1.0", '{"foo": "bar"}')
    mock_response = Mock(status_code=201, text="Created", elapsed=Mock(total_seconds=lambda: 0.2))
    with patch("requests.post", return_value=mock_response):
        api_frame.send_request()
    assert "Status Code: 201" in api_frame.response_text.get("1.0", tk.END)
    assert "Created" in api_frame.response_text.get("1.0", tk.END)

def test_send_post_request_with_invalid_json(api_frame):
    api_frame.url_entry.insert(0, "http://test.com")
    api_frame.method_var.set("POST")
    api_frame.body_text.insert("1.0", '{"foo": bar}')  # invalid JSON
    api_frame.send_request()
    assert "Invalid JSON format" in api_frame.response_text.get("1.0", tk.END)

def test_send_put_request_with_valid_json(api_frame):
    api_frame.url_entry.insert(0, "http://test.com")
    api_frame.method_var.set("PUT")
    api_frame.body_text.insert("1.0", '{"foo": "baz"}')
    mock_response = Mock(status_code=200, text="Updated", elapsed=Mock(total_seconds=lambda: 0.3))
    with patch("requests.put", return_value=mock_response):
        api_frame.send_request()
    assert "Status Code: 200" in api_frame.response_text.get("1.0", tk.END)
    assert "Updated" in api_frame.response_text.get("1.0", tk.END)

def test_send_delete_request_success(api_frame):
    api_frame.url_entry.insert(0, "http://test.com")
    api_frame.method_var.set("DELETE")
    mock_response = Mock(status_code=204, text="", elapsed=Mock(total_seconds=lambda: 0.05))
    with patch("requests.delete", return_value=mock_response):
        api_frame.send_request()
    assert "Status Code: 204" in api_frame.response_text.get("1.0", tk.END)

def test_send_request_unsupported_method(api_frame):
    api_frame.url_entry.insert(0, "http://test.com")
    api_frame.method_var.set("PATCH")  # Not supported
    api_frame.send_request()
    assert "Unsupported method" in api_frame.response_text.get("1.0", tk.END)

def test_send_request_exception(api_frame):
    api_frame.url_entry.insert(0, "http://test.com")
    api_frame.method_var.set("GET")
    with patch("requests.get", side_effect=Exception("Network error")):
        api_frame.send_request()
    assert "Error: Network error" in api_frame.response_text.get("1.0", tk.END)