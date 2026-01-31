#!/usr/bin/env python3
"""Check API key in database for SDXL model"""
import sys
import os

# Add ai-workspace-app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-workspace-app'))

from app import app # type: ignore
from models import db, GenerativeModel # type: ignore

with app.app_context():
    model = db.session.get(GenerativeModel, 1)
    if model:
        print(f"Model: {model.name}")
        print(f"Display Name: {model.display_name}")
        print(f"API Key: {model.api_key}")
        print(f"API URL: {model.api_url}")
    else:
        print("Model not found!")
