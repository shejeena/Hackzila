import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys

# Mock external modules
sys.modules['dbconnector'] = MagicMock()
sys.modules['auth_config'] = MagicMock()
sys.modules['httpx'] = MagicMock()

import tkinter as tk
from db_mapping_ui import DBFormApp

class TestDBFormApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window

        # Mock DBConnector
        self.mock_dbconnector = MagicMock()
        self.mock_dbconnector.get_connection.return_value = True
        self.mock_dbconnector.get_table_names.return_value = ['patients']
        self.mock_dbconnector.get_table_columns.return_value = [
            ('patient_id', 'int'),
            ('first_name', 'varchar'),
            ('last_name', 'varchar'),
            ('date_of_birth', 'date')
        ]

        # Patch DBConnector to return our mock
        patcher_db = patch('db_mapping_ui.DBConnector', return_value=self.mock_dbconnector)
        self.addCleanup(patcher_db.stop)
        self.mock_DBConnector = patcher_db.start()

        # Mock ApiAuth
        self.mock_auth = MagicMock()
        self.mock_auth.build_headers.return_value = {'Authorization': 'Bearer testtoken'}
        self.mock_auth.build_basic_auth.return_value = ('user', 'pass')

        # Patch PhotoImage to avoid file errors
        patcher_img = patch('db_mapping_ui.PhotoImage', return_value=MagicMock())
        self.addCleanup(patcher_img.stop)
        patcher_img.start()

    def tearDown(self):
        self.root.destroy()

    def test_initialization_and_ui(self):
        app = DBFormApp(self.root, 'PostgreSQL', MagicMock(), self.mock_auth)
        self.assertIsInstance(app, DBFormApp)
        self.assertEqual(app.dbtype, 'PostgreSQL')
        self.assertIs(app.auth, self.mock_auth)
        self.assertIsNotNone(app.table_dropdown)
        self.assertIn('patients', app.table_dropdown['values'])

    def test_validate_inputs_valid(self):
        app = DBFormApp(self.root, 'PostgreSQL', MagicMock(), self.mock_auth)
        app.table_var.set('patients')
        # Simulate user input
        for col in ['patient_id', 'first_name', 'last_name', 'date_of_birth']:
            entry = MagicMock()
            entry.get.return_value = '123' if col == 'patient_id' else 'John' if col == 'first_name' else 'Doe' if col == 'last_name' else '2000-01-01'
            app.inputs[col] = entry
        errors = app.validate_inputs()
        self.assertEqual(errors, [])

    def test_validate_inputs_invalid(self):
        app = DBFormApp(self.root, 'PostgreSQL', MagicMock(), self.mock_auth)
        app.table_var.set('patients')
        # Simulate invalid input for patient_id and date_of_birth
        app.inputs['patient_id'] = MagicMock(get=MagicMock(return_value='abc'))
        app.inputs['date_of_birth'] = MagicMock(get=MagicMock(return_value='01-01-2000'))
        app.inputs['first_name'] = MagicMock(get=MagicMock(return_value='John'))
        app.inputs['last_name'] = MagicMock(get=MagicMock(return_value='Doe'))
        errors = app.validate_inputs()
        self.assertIn('patient_id must be an integer.', errors)
        self.assertIn('date_of_birth must be YYYY-MM-DD.', errors)

    @patch('db_mapping_ui.httpx.AsyncClient', new_callable=AsyncMock)
    def test_perform_request(self, mock_async_client):
        app = DBFormApp(self.root, 'PostgreSQL', MagicMock(), self.mock_auth)
        app.method_var.set('GET')
        app.api_path_var.set('http://localhost/api/patients')
        app.inputs = {
            'patient_id': MagicMock(get=MagicMock(return_value='1')),
            'first_name': MagicMock(get=MagicMock(return_value='')),
            'last_name': MagicMock(get=MagicMock(return_value='')),
            'date_of_birth': MagicMock(get=MagicMock(return_value=''))
        }
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'ok'}
        mock_response.status_code = 200
        mock_response.text = '{"result": "ok"}'
        mock_async_client().__aenter__().get.return_value = mock_response

        # Patch _update_response to avoid UI calls
        app._update_response = MagicMock()

        import asyncio
        asyncio.run(app._perform_request())
        app._update_response.assert_called()
        args = app._update_response.call_args[0][0]
        self.assertIn('Status: 200', args)
        self.assertIn('"result": "ok"', args)

if __name__ == "__main__":
    unittest.main()