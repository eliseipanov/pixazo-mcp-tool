#!/usr/bin/env python3
"""
Migration script to add slug column to workspaces table
"""
import sys
import os

# Add parent directory to path to import from ai-workspace-app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-workspace-app'))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Workspace, generate_slug

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/pixazo/ai-workspace-app/db/workspace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    # Check if slug column already exists
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('workspaces')]
    
    if 'slug' not in columns:
        print("Adding slug column to workspaces table...")
        
        # Add slug column using raw SQL
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE workspaces ADD COLUMN slug VARCHAR(100) NOT NULL DEFAULT 'workspace'"))
            conn.commit()
        
        print("Slug column added successfully.")
        
        # Generate slugs for existing workspaces
        print("Generating slugs for existing workspaces...")
        workspaces = Workspace.query.all()
        
        for workspace in workspaces:
            # Generate slug from name
            slug = generate_slug(workspace.name)
            
            # Check if slug already exists for this user
            existing = Workspace.query.filter(
                Workspace.user_id == workspace.user_id,
                Workspace.slug == slug,
                Workspace.id != workspace.id
            ).first()
            
            if existing:
                # Append a number to make it unique
                counter = 1
                while Workspace.query.filter(
                    Workspace.user_id == workspace.user_id,
                    Workspace.slug == f"{slug}-{counter}",
                    Workspace.id != workspace.id
                ).first():
                    counter += 1
                slug = f"{slug}-{counter}"
            
            workspace.slug = slug
            print(f"  Workspace '{workspace.name}' -> slug: '{slug}'")
        
        db.session.commit()
        print(f"Generated slugs for {len(workspaces)} workspaces.")
    else:
        print("Slug column already exists in workspaces table.")
        
        # Check for workspaces without slugs
        workspaces_without_slug = Workspace.query.filter(Workspace.slug == None).all()
        if workspaces_without_slug:
            print(f"Found {len(workspaces_without_slug)} workspaces without slugs. Generating...")
            
            for workspace in workspaces_without_slug:
                slug = generate_slug(workspace.name)
                
                # Check if slug already exists for this user
                existing = Workspace.query.filter(
                    Workspace.user_id == workspace.user_id,
                    Workspace.slug == slug,
                    Workspace.id != workspace.id
                ).first()
                
                if existing:
                    # Append a number to make it unique
                    counter = 1
                    while Workspace.query.filter(
                        Workspace.user_id == workspace.user_id,
                        Workspace.slug == f"{slug}-{counter}",
                        Workspace.id != workspace.id
                    ).first():
                        counter += 1
                    slug = f"{slug}-{counter}"
                
                workspace.slug = slug
                print(f"  Workspace '{workspace.name}' -> slug: '{slug}'")
            
            db.session.commit()
            print(f"Generated slugs for {len(workspaces_without_slug)} workspaces.")
        else:
            print("All workspaces have slugs.")

print("Migration completed successfully!")
