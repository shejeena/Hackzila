import unittest
from unittest.mock import patch, MagicMock
import sys

sys.modules['api_test_ui'] = MagicMock()
sys.modules['dbconnector'] = MagicMock()
sys.modules['db_mapping_ui'] = MagicMock()
sys.modules['auth_config'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()

import tkinter as tk
from Hackzilla import HackzillaApp

class TestHackzillaApp(unittest.TestCase):
    def setUp(self):
        # Patch Tkinter root so no real window is created
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window

    def tearDown(self):
        self.root.destroy()

    @patch('Hackzilla.DBFormApp')
    @patch('Hackzilla.AuthConfigUI')
    def test_app_initialization(self, MockAuthConfigUI, MockDBFormApp):
        # Mock AuthConfigUI and its .auth property
        mock_auth_ui = MagicMock()
        mock_auth_ui.auth = MagicMock()
        MockAuthConfigUI.return_value = mock_auth_ui

        app = HackzillaApp(self.root)

        # Check notebook and tabs exist
        self.assertIsNotNone(app.notebook)
        self.assertIsNotNone(app.db_tab)
        self.assertIsNotNone(app.api_key_tab)
        self.assertIsNotNone(app.api_tab)

        # AuthConfigUI should be initialized and packed
        MockAuthConfigUI.assert_called_with(app.api_key_tab)
        mock_auth_ui.frame.pack.assert_called()

        # DBFormApp should be initialized with correct auth
        app.connection = MagicMock()
        app.db_type_var.set("PostgreSQL")
        app.load_db_ui()
        MockDBFormApp.assert_called_with(
            app.db_tab,
            "PostgreSQL",
            app.connection,
            auth=mock_auth_ui.auth
        )
        app.db_ui_frame.pack.assert_called()

    @patch('Hackzilla.psycopg2.connect')
    def test_connect_to_db_success(self, mock_connect):
        app = HackzillaApp(self.root)
        app.db_type_var.set("PostgreSQL")
        app.host_entry.get = MagicMock(return_value="localhost")
        app.port_entry.get = MagicMock(return_value="5432")
        app.user_entry.get = MagicMock(return_value="admin")
        app.password_entry.get = MagicMock(return_value="password")
        app.db_name_entry.get = MagicMock(return_value="patientdb")

        mock_connect.return_value = MagicMock()
        with patch('tkinter.messagebox.showinfo') as mock_info:
            app.connect_to_db()
            mock_info.assert_called_with("Success", "Connected to the database!")
            self.assertIsNotNone(app.connection)

    @patch('Hackzilla.psycopg2.connect', side_effect=Exception("fail"))
    def test_connect_to_db_failure(self, mock_connect):
        app = HackzillaApp(self.root)
        app.db_type_var.set("PostgreSQL")
        app.host_entry.get = MagicMock(return_value="localhost")
        app.port_entry.get = MagicMock(return_value="5432")
        app.user_entry.get = MagicMock(return_value="admin")
        app.password_entry.get = MagicMock(return_value="password")
        app.db_name_entry.get = MagicMock(return_value="patientdb")

        with patch('tkinter.messagebox.showerror') as mock_error:
            app.connect_to_db()
            mock_error.assert_called()
            self.assertIsNone(app.connection)

if __name__ == "__main__":
    unittest.main()                             