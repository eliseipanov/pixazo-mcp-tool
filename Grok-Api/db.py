import sqlite3
from datetime import datetime, timedelta
import secrets

# Initialize the database
conn = sqlite3.connect('api_users.db')
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
    cursor.execute(
        "SELECT expiring_date FROM api_users WHERE api_key = ?",
        (api_key,)
    )
    result = cursor.fetchone()
    
    if not result:
        return False
    
    expiring_date = result[0]
    if expiring_date:
        if datetime.now() > datetime.fromisoformat(expiring_date):
            return False
    
    return True

# Close the database connection when done
# conn.close()