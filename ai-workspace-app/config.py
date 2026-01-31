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

# Grok-Api configuration
GROK_API_URL = os.environ.get('GROK_API_URL', 'http://localhost:6969')
GROK_API_KEY = os.environ.get('GROK_API_KEY', '')

# Image generation models configuration
IMAGE_GENERATION_MODELS = {
    'sdxl': {
        'name': 'SDXL (Stable Diffusion XL)',
        'default_width': 768,
        'default_height': 1024,
        'default_steps': 20,
        'default_guidance_scale': 8.0,
        'max_width': 1536,
        'max_height': 2048,
        'min_steps': 10,
        'max_steps': 50,
        'min_guidance_scale': 1.0,
        'max_guidance_scale': 20.0
    },
    'flux': {
        'name': 'Flux Klein',
        'default_width': 768,
        'default_height': 1024,
        'default_steps': 20,
        'default_guidance_scale': 8.0,
        'max_width': 1536,
        'max_height': 2048,
        'min_steps': 10,
        'max_steps': 50,
        'min_guidance_scale': 1.0,
        'max_guidance_scale': 20.0
    }
}
