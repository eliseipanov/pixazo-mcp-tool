#!/usr/bin/env python
# migrate_add_model_column.py
"""
Migration script to add 'model' column to styles table.
Run this to update existing database with new model field.
"""

from app import app
from models import db, Style


def migrate_add_model_column():
    """Add model column to styles table if it doesn't exist"""
    with app.app_context():
        # Check if model column exists
        inspector = db.inspect(db.engine)
        
        # Check if styles table exists
        if 'styles' in inspector.get_table_names():
            existing_columns = [col['name'] for col in inspector.get_columns('styles')]
            
            print(f"Existing columns in styles table: {existing_columns}")
            
            if 'model' not in existing_columns:
                print("Adding 'model' column to styles table...")
                
                # Add the column with default value 'sdxl'
                with db.engine.connect() as conn:
                    conn.execute(db.text("""
                        ALTER TABLE styles 
                        ADD COLUMN model VARCHAR(50) DEFAULT 'sdxl'
                    """))
                
                print("✓ 'model' column added successfully")
                
                # Update existing styles to have default model
                styles_without_model = Style.query.filter_by(model=None).all()
                if styles_without_model:
                    print(f"Updating {len(styles_without_model)} existing styles with default model...")
                    for style in styles_without_model:
                        style.model = 'sdxl'
                    db.session.commit()
                    print(f"✓ Updated {len(styles_without_model)} styles with default model 'sdxl'")
            else:
                print("✓ 'model' column already exists")
        else:
            print("✗ styles table not found")
        
        print("\n✓ Migration completed!")


if __name__ == '__main__':
    migrate_add_model_column()
