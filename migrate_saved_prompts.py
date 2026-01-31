#!/usr/bin/env python3
"""
Migration script to create saved_prompts table
"""
import sys
import os

# Add parent directory to path to import from ai-workspace-app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-workspace-app'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, SavedPrompt

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/pixazo/ai-workspace-app/db/workspace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    # Check if saved_prompts table already exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'saved_prompts' not in tables:
        print("Creating saved_prompts table...")
        db.create_all()
        print("saved_prompts table created successfully.")
    else:
        print("saved_prompts table already exists.")

print("Migration completed successfully!")
