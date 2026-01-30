#!/usr/bin/env python
# init_db.py
"""
Initialize the database with a test user and sample data.
Run this script to set up the database for development.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app
from models import db, User, Workspace, Theme, Style, ChatMessage, GeneratedImage


def init_database():
    """Initialize the database with sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")

        # Check if test user already exists
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('testpass123')
            )
            db.session.add(test_user)
            db.session.commit()
            print("✓ Test user created (username: testuser, password: testpass123)")
        else:
            print("✓ Test user already exists")

        # Create sample themes
        if Theme.query.count() == 0:
            themes = [
                Theme(
                    name='Photorealistic',
                    base_prompt='photorealistic, highly detailed, 8k, professional photography',
                    description='For generating photorealistic images with high detail'
                ),
                Theme(
                    name='Digital Art',
                    base_prompt='digital art, vibrant colors, stylized, concept art',
                    description='For creating digital artwork and concept art'
                ),
                Theme(
                    name='Anime Style',
                    base_prompt='anime style, manga, vibrant, detailed illustration',
                    description='For generating anime and manga style artwork'
                )
            ]
            for theme in themes:
                db.session.add(theme)
            db.session.commit()
            print(f"✓ Created {len(themes)} sample themes")
        else:
            print("✓ Themes already exist")

        # Create sample workspace
        if Workspace.query.filter_by(user_id=test_user.id).count() == 0:
            workspace = Workspace(
                name='My First Workspace',
                description='A workspace for testing AI image generation',
                user_id=test_user.id,
                theme_id=Theme.query.first().id
            )
            db.session.add(workspace)
            db.session.commit()
            print("✓ Created sample workspace")

            # Create sample style
            style = Style(
                name='Default Style',
                positive_prompt='beautiful landscape, mountains, sunset, dramatic lighting',
                negative_prompt='blurry, low quality, distorted, ugly',
                cfg_scale=7.5,
                steps=25,
                seed=42,
                workspace_id=workspace.id
            )
            db.session.add(style)
            db.session.commit()
            print("✓ Created sample style")

            # Create sample chat messages
            messages = [
                ChatMessage(
                    workspace_id=workspace.id,
                    role='user',
                    content='Can you help me create a beautiful landscape image?'
                ),
                ChatMessage(
                    workspace_id=workspace.id,
                    role='assistant',
                    content='Of course! I can help you create a beautiful landscape. Let me suggest some prompts for you.'
                )
            ]
            for msg in messages:
                db.session.add(msg)
            db.session.commit()
            print("✓ Created sample chat messages")
        else:
            print("✓ Workspace already exists")

        print("\n✓ Database initialization complete!")
        print("\nYou can now:")
        print("  1. Login with username: testuser, password: testpass123")
        print("  2. Create workspaces, themes, and styles")
        print("  3. Start generating AI images")


if __name__ == '__main__':
    init_database()
