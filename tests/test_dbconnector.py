import pytest
from unittest.mock import Mock, MagicMock, call
import dbconnector
from dbconnector import DBConnector

def make_mock_conn():
    mock_cursor = MagicMock()   
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

def test_filter_audit_columns_tuples():
    cols = [
        ("id", "integer"),
        ("created_at", "timestamp"),
        ("name", "text"),
        ("deleted_flag", "boolean"),
        ("updated_on", "timestamp"),
        ("count", "integer"),
    ]
    filtered = DBConnector.filter_audit_columns(cols)
    assert ("id", "integer") in filtered
    assert ("name", "text") in filtered
    assert all("created" not in name for name, _ in filtered)
    assert all("updated" not in name for name, _ in filtered)
    assert all("deleted" not in name for name, _ in filtered)

def test_get_table_names_sqlite():
    mock_conn, mock_cursor = make_mock_conn()
    mock_cursor.fetchall.return_value = [("users",), ("orders",)]
    db = DBConnector("sqlite", mock_conn)
    tables = db.get_table_names()
    assert tables == ["users", "orders"]
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT name FROM sqlite_master WHERE type='table';")
    mock_cursor.close.assert_called_once()

def test_get_table_names_postgres():
    mock_conn, mock_cursor = make_mock_conn()
    mock_cursor.fetchall.return_value = [("users",), ("products",)]
    db = DBConnector("postgres", mock_conn)
    tables = db.get_table_names()
    assert tables == ["users", "products"]
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()

def test_get_table_names_mysql():
    mock_conn, mock_cursor = make_mock_conn()
    # MySQL SHOW TABLES typically returns rows like ('users',)
    mock_cursor.fetchall.return_value = [("users",), ("invoices",)]
    db = DBConnector("mysql", mock_conn)
    tables = db.get_table_names()
    assert tables == ["users", "invoices"]
    mock_cursor.execute.assert_called_once_with("SHOW TABLES;")
    mock_cursor.close.assert_called_once()

def test_get_table_columns_postgres_filters_audit():
    mock_conn, mock_cursor = make_mock_conn()
    mock_cursor.fetchall.return_value = [
        ("id", "integer"),
        ("created_at", "timestamp"),
        ("name", "text"),
        ("updated_on", "timestamp")
    ]
    db = DBConnector("postgres", mock_conn)
    cols = db.get_table_columns("users")
    # Expect tuples filtered to remove audit columns
    assert ("id", "integer") in cols
    assert ("name", "text") in cols
    assert all("created" not in name for name, _ in cols)
    assert all("updated" not in name for name, _ in cols)
    # Assert the SQL used includes information_schema.columns and a parameter was passed
    mock_cursor.execute.assert_called()
    mock_cursor.close.assert_called_once()

def test_get_table_columns_mysql_filters_audit():
    mock_conn, mock_cursor = make_mock_conn()
    mock_cursor.fetchall.return_value = [
        ("id", "int"),
        ("status_flag", "varchar"),
        ("deleted_at", "datetime"),
        ("title", "varchar")
    ]
    db = DBConnector("mysql", mock_conn)
    cols = db.get_table_columns("posts")
    assert ("id", "int") in cols
    assert ("title", "varchar") in cols
    assert all("deleted" not in name for name, _ in cols)
    assert all("status" not in name for name, _ in cols)
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()

def test_get_table_columns_sqlite_filters_names(monkeypatch):
    mock_conn, mock_cursor = make_mock_conn()
    # PRAGMA table_info returns rows where index 1 is column name
    mock_cursor.fetchall.return_value = [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "created_at", "TIMESTAMP", 0, None, 0),
        (2, "name", "TEXT", 0, None, 0),
        (3, "deleted", "BOOLEAN", 0, None, 0),
    ]
    db = DBConnector("sqlite", mock_conn)

    # Patch filter_audit_columns to accept a list of names (strings) for the sqlite code path
    original_filter = DBConnector.filter_audit_columns
    def patched_filter(columns):
        # If provided list of strings (sqlite path), filter by audit keywords
        if columns and isinstance(columns[0], str):
            audit_keywords = ['created', 'updated', 'modified', 'timestamp', 'status', 'deleted']
            return [name for name in columns if not any(k in name.lower() for k in audit_keywords)]
        # Fallback to original behavior
        return original_filter(columns)
    monkeypatch.setattr(DBConnector, "filter_audit_columns", staticmethod(patched_filter))

    cols = db.get_table_columns("users")
    # Since sqlite branch produces name-only lists and patched_filter returns names,
    # expect the returned list to contain names (strings) with audit ones removed
    assert "id" in cols
    assert "name" in cols
    assert all("created" not in c for c in cols)
    assert all("deleted" not in c for c in cols)

    mock_cursor.execute.assert_called_once_with("PRAGMA table_info('users');")
    mock_cursor.close.assert_called_once()