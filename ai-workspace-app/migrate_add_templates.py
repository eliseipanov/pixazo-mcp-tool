#!/usr/bin/env python3
"""
Migration script to add request_template and response_template columns to generative_models table.
Run this script to update the database schema.
"""

import os
import sys

# Change to ai-workspace-app directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from app import app, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Add request_template and response_template columns to generative_models table."""
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('generative_models')]
            
            if 'request_template' in columns and 'response_template' in columns:
                logger.info("Columns already exist. Migration not needed.")
                return
            
            # Add columns if they don't exist
            if 'request_template' not in columns:
                logger.info("Adding request_template column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text(
                        "ALTER TABLE generative_models ADD COLUMN request_template TEXT"
                    ))
                logger.info("request_template column added.")
            
            if 'response_template' not in columns:
                logger.info("Adding response_template column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text(
                        "ALTER TABLE generative_models ADD COLUMN response_template TEXT"
                    ))
                logger.info("response_template column added.")
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


if __name__ == '__main__':
    migrate()
