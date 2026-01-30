#!/usr/bin/env python
# test_db.py
"""
Test script to verify database is working correctly.
"""

from app import app
from models import db, User


def test_database():
    """Test database connection and user creation"""
    with app.app_context():
        # Create tables
        db.create_all()
        print("✓ Database tables created/verified")
        
        # Count users
        user_count = User.query.count()
        print(f"✓ Current user count: {user_count}")
        
        # List all users
        users = User.query.all()
        if users:
            print("\n✓ Existing users:")
            for user in users:
                print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")
        else:
            print("\n✓ No users found in database")
        
        # Test creating a user
        print("\n✓ Testing user creation...")
        test_user = User(
            username='test_db_user',
            email='testdb@example.com',
            password_hash='test_hash'
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"✓ Test user created with ID: {test_user.id}")
        
        # Verify user was created
        new_count = User.query.count()
        print(f"✓ New user count: {new_count}")
        
        # Clean up test user
        db.session.delete(test_user)
        db.session.commit()
        print(f"✓ Test user deleted")
        
        final_count = User.query.count()
        print(f"✓ Final user count: {final_count}")
        
        print("\n✓ Database test completed successfully!")


if __name__ == '__main__':
    test_database()
