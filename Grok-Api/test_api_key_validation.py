import unittest
import sqlite3
from datetime import datetime, timedelta
from db import validate_api_key, add_api_key

class TestAPIKeyValidation(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize the database
        cls.conn = sqlite3.connect(':memory:')
        cls.cursor = cls.conn.cursor()
        
        # Create the api_users table
        cls.cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT NOT NULL,
            expiring_date TEXT
        )
        ''')
        cls.conn.commit()
        
        # Add a test API key
        cls.test_api_key = "test_api_key_123"
        cls.cursor.execute(
            "INSERT INTO api_users (api_key, expiring_date) VALUES (?, ?)",
            (cls.test_api_key, None)
        )
        cls.conn.commit()
        
    def test_validate_api_key(self):
        # Test with a valid API key
        self.assertTrue(validate_api_key(self.test_api_key))
        
        # Test with an invalid API key
        self.assertFalse(validate_api_key("invalid_api_key"))
        
    def test_validate_api_key_with_expiration(self):
        # Add a test API key with an expiration date
        expiring_date = (datetime.now() + timedelta(days=1)).isoformat()
        self.cursor.execute(
            "INSERT INTO api_users (api_key, expiring_date) VALUES (?, ?)",
            ("test_api_key_expired", expiring_date)
        )
        self.conn.commit()
        
        # Test with a valid API key with expiration date
        self.assertTrue(validate_api_key("test_api_key_expired"))
        
        # Test with an expired API key
        expired_date = (datetime.now() - timedelta(days=1)).isoformat()
        self.cursor.execute(
            "INSERT INTO api_users (api_key, expiring_date) VALUES (?, ?)",
            ("test_api_key_expired", expired_date)
        )
        self.conn.commit()
        
        self.assertFalse(validate_api_key("test_api_key_expired"))
        
    @classmethod
    def tearDownClass(cls):
        # Close the database connection
        cls.conn.close()

if __name__ == '__main__':
    unittest.main()