# config.py
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database configuration
DB_DIR = BASE_DIR / 'db'
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / 'workspace.db'

SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key (change in production)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me-in-production')

# Upload directories
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)
IMAGES_DIR = UPLOAD_DIR / 'images'
IMAGES_DIR.mkdir(exist_ok=True)
THUMBNAILS_DIR = UPLOAD_DIR / 'thumbnails'
THUMBNAILS_DIR.mkdir(exist_ok=True)
