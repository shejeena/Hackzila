import pytest
from unittest.mock import Mock
import dbconnector
from dbconnector import DBConnector

def test_get_connection_returns_same_for_sqlite():
    mock_cursor = Mock()
    mock_cursor.execute = Mock()
    mock_cursor.fetchall = Mock(return_value=[("tbl",)])
    mock_conn = Mock()
    # Provide a `cursor` attribute (not a method) because the current implementation does `self.conn.cursor`
    mock_conn.cursor = mock_cursor

    dbc = DBConnector("sqlite", mock_conn)

    mock_cursor.execute.assert_called_once_with("SELECT name FROM sqlite_master WHERE type='table';")
    mock_cursor.fetchall.assert_called_once()
    assert dbc.get_connection() is mock_conn

def test_sqlite_with_cursor_object_not_method():
    # If a connection exposes a cursor object via attribute, DBConnector should use it (this mirrors current code)
    mock_cursor = Mock()
    mock_cursor.execute = Mock()
    mock_cursor.fetchall = Mock(return_value=[])
    class Conn:
        def __init__(self):
            self.cursor = mock_cursor
    conn_obj = Conn()

    dbc = DBConnector("SQLite", conn_obj)

    mock_cursor.execute.assert_called_once()
    assert dbc.get_connection() is conn_obj

def test_unsupported_db_type_raises_value_error():
    with pytest.raises(ValueError):
        DBConnector("oracle", Mock())

def test_postgresql_uses_config_and_calls_psycopg2_connect(monkeypatch):
    # Arrange: provide a module-level config and replace psycopg2.connect
    captured = {}
    def fake_connect(**kwargs):
        captured.update(kwargs)
        return "pg_connection_object"

    monkeypatch.setattr(dbconnector, "config", {"database": "db", "user": "u", "password": "p", "host": "h"})
    monkeypatch.setattr(dbconnector.psycopg2, "connect", fake_connect)

    # Act
    dbc = DBConnector("PostgreSQL", None)

    # Assert
    assert dbc.get_connection() == "pg_connection_object"
    assert captured["dbname"] == "db"
    assert captured["user"] == "u"
    assert captured["host"] == "h"

def test_mysql_uses_config_and_calls_mysql_connector_connect(monkeypatch):
    captured = {}
    def fake_connect(**kwargs):
        captured.update(kwargs)
        return "mysql_connection_object"

    monkeypatch.setattr(dbconnector, "config", {"database": "db", "user": "u", "password": "p", "host": "h"})
    # dbconnector imported mysql.connector as `mysql.connector` so patch that target
    monkeypatch.setattr(dbconnector.mysql.connector, "connect", fake_connect)

    dbc = DBConnector("MySQL", None)

    assert dbc.get_connection() == "mysql_connection_object"
    assert captured["database"] == "db"
    assert captured["user"] == "u"