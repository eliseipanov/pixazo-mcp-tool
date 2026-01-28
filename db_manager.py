import sqlite3
import json
from datetime import datetime
from config import Config

def initialize_db(db_path: str = None):
    """
    Initialize the SQLite database and create the generations table.
    
    Args:
        db_path (str): Path to the SQLite database file. If None, uses Config.DATABASE_PATH.
    """
    if db_path is None:
        db_path = Config.DATABASE_PATH
    
    try:
        # Ensure the directory exists
        import os
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the generations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generations (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                prompt TEXT NOT NULL,
                parameters_json TEXT,
                image_url TEXT,
                status TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized successfully at {db_path}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def save_metadata(db_path: str, data: dict):
    """
    Save generation metadata to the database.
    
    Args:
        db_path (str): Path to the SQLite database file
        data (dict): Dictionary containing metadata with keys:
            - timestamp: str
            - prompt: str
            - parameters_json: dict or str
            - image_url: str (optional)
            - status: str
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Convert parameters to JSON string if it's a dict
        parameters_json = data.get('parameters_json', {})
        if isinstance(parameters_json, dict):
            parameters_json = json.dumps(parameters_json)
        
        # Insert the metadata
        cursor.execute('''
            INSERT INTO generations (timestamp, prompt, parameters_json, image_url, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['timestamp'],
            data['prompt'],
            parameters_json,
            data.get('image_url'),
            data['status']
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error saving metadata: {e}")
        raise

if __name__ == "__main__":
    # Initialize database when module is run directly
    initialize_db()
