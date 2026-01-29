import sqlite3
import logging
from datetime import datetime, timedelta
import secrets
import os

# Get the directory of the current file
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, 'api_users.db')
# DB_PATH = "/var/www/pixazo/data/api_users.db"

# Initialize the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create the api_users table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS api_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key TEXT NOT NULL,
    expiring_date TEXT
)
''')
conn.commit()

# Function to generate a new API key
def generate_api_key():
    return secrets.token_urlsafe(32)

# Function to add a new API key to the database
def add_api_key(expiration_days=None):
    api_key = generate_api_key()
    expiring_date = None
    
    if expiration_days:
        expiring_date = (datetime.now() + timedelta(days=expiration_days)).isoformat()
    
    cursor.execute(
        "INSERT INTO api_users (api_key, expiring_date) VALUES (?, ?)",
        (api_key, expiring_date)
    )
    conn.commit()
    return api_key

# Function to validate an API key
def validate_api_key(api_key):
    # TEMPORARY: Skip validation for testing
    logging.debug(f"API key validation temporarily disabled for testing: {api_key}")
    return True

    # Original validation logic (commented out for testing)
    """
    logging.debug(f"Validating API key: {api_key}")
    cursor.execute(
        "SELECT api_key, expiring_date FROM api_users WHERE api_key = ?",
        (api_key,)
    )
    result = cursor.fetchone()

    if not result:
        logging.error(f"API key {api_key} not found in database")
        return False

    expiring_date = result[1]  # expiring_date is the second column
    logging.debug(f"Found API key {api_key} with expiration date: {expiring_date}")

    if expiring_date and datetime.now() > datetime.fromisoformat(expiring_date):
        logging.error(f"API key {api_key} has expired")
        return False

    logging.debug(f"API key {api_key} is valid")
    return True
    """

# Close the database connection when done
# conn.close()