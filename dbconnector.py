import psycopg2
import mysql.connector

class DBConnector:
    def __init__(self, db_type, connection):
        self.conn = connection
        self.db_type = db_type.lower()

    @staticmethod
    def filter_audit_columns(columns):
        audit_keywords = ['created', 'updated', 'modified', 'timestamp', 'status', 'deleted']
        return [
            (name, dtype) for name, dtype in columns
            if not any(keyword in name.lower() for keyword in audit_keywords)
        ]

    def get_table_names(self):
        """
        Return a list of table names for the configured database type.
        Expects `self.conn` to provide a `.cursor()` method that supports `.execute()` and `.fetchall()`.
        """
        cursor = self.conn.cursor()
        try:
            if self.db_type == "sqlite":
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            elif self.db_type in ("postgresql", "postgres"):
                cursor.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
                )
            elif self.db_type == "mysql":
                cursor.execute("SHOW TABLES;")
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")

            rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def get_connection(self):
        return self.conn

    def get_table_columns(self, table_name):
        """
        Returns a list of column names for the specified table in the given database.
        """
        cursor = self.conn.cursor()
        try:
            if self.db_type == "sqlite":
                cursor.execute(f"PRAGMA table_info('{table_name}');")
                columns = [col[1] for col in cursor.fetchall()]
                return self.filter_audit_columns(columns)
            elif self.db_type in ("postgresql", "postgres"):
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s;""", (table_name,))
                columns = cursor.fetchall()
                print(self.filter_audit_columns(columns))
                return self.filter_audit_columns(columns)
            elif self.db_type == "mysql":
                query = """SELECT column_name, data_type
                           FROM information_schema.columns
                           WHERE table_name = %s;"""
                cursor.execute(query, (table_name,))
                columns = cursor.fetchall()
                print(self.filter_audit_columns(columns))
                return self.filter_audit_columns(columns)
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        finally:
            try:
                cursor.close()
            except Exception:
                pass
