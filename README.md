# Hackzila
A platform for interactive API Testing

# Database Mapping & API UI Toolkit

A Python toolkit for building database-driven UI applications with REST API integration. This project provides reusable components for connecting to SQL databases, mapping tables and columns, and managing authentication for API requests. The UI is built using Tkinter and supports PostgreSQL, MySQL, and SQLite.

## Features

- **DBConnector**: Unified interface for fetching table names and columns from PostgreSQL, MySQL, or SQLite databases.
- **DBFormApp**: Tkinter-based form for mapping database tables to REST API endpoints, sending requests, and exporting responses.
- **ApiAuth**: Flexible authentication manager supporting bearer tokens, API keys, and basic auth.
- **AuthConfigUI**: Tkinter UI for configuring and previewing API authentication.
- **CSV/XLSX Import/Export**: Download and upload table data in CSV or Excel format.
- **Request History**: Save and view the last 50 API requests and responses.
- **Audit Column Filtering**: Automatically excludes audit fields (created, updated, etc.) from input forms.

## Requirements

- Python 3.8+
- `psycopg2` (PostgreSQL)
- `mysql-connector-python` (MySQL)
- `httpx`
- `openpyxl` (for XLSX support)
- `pytest` (for running tests)

Install dependencies:
pip install psycopg2 mysql-connector-python httpx openpyxl pytest

## Usage

1. **Configure your database connection** in your main script and instantiate `DBConnector`:
    ```python
    from dbconnector import DBConnector
    import psycopg2

    conn = psycopg2.connect(database="mydb", user="user", password="pass")
    db = DBConnector("postgresql", conn)
    tables = db.get_table_names()
    columns = db.get_table_columns("my_table")
    ```

2. **Launch the UI**:
    ```python
    from db_mapping_ui import DBFormApp
    import tkinter as tk

    root = tk.Tk()
    app = DBFormApp(root, "postgresql", conn)
    root.mainloop()
    ```

3. **Configure API authentication** using the AuthConfigUI or directly via ApiAuth.

## Project Structure

- `dbconnector.py` — Database abstraction for table/column metadata.
- `db_mapping_ui.py` — Main Tkinter UI for mapping and API requests.
- `auth_config.py` — Authentication logic and configuration UI.
- `Hackzilla.py` — Example or main application entry point.
- `tests/` — Unit tests for core modules.

## Testing

Run unit tests with:
pytest tests/