# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import re

db = SQLAlchemy()


def generate_slug(name: str) -> str:
    """Generate a URL-safe slug from a name."""
    # Convert to lowercase
    slug = name.lower()
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Ensure slug is not empty
    if not slug:
        slug = 'workspace'
    return slug


class User(UserMixin, db.Model):
    """User model for authentication and workspace ownership"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, default=False)  # Superuser can manage models

    # Relationships
    workspaces = db.relationship('Workspace', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Workspace(db.Model):
    """Workspace model for organizing AI generation sessions"""
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)  # URL-safe version of name
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    theme = db.relationship('Theme', backref='workspaces')
    styles = db.relationship('Style', backref='workspace', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='workspace', lazy=True, cascade='all, delete-orphan')
    generated_images = db.relationship('GeneratedImage', backref='workspace', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Workspace {self.name}>'


class Theme(db.Model):
    """Theme model for base prompts and descriptions"""
    __tablename__ = 'themes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_prompt = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Theme {self.name}>'


class Style(db.Model):
    """Style model for generation parameters"""
    __tablename__ = 'styles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    positive_prompt = db.Column(db.Text, nullable=False)
    negative_prompt = db.Column(db.Text, nullable=True)
    cfg_scale = db.Column(db.Float, default=7.0)
    steps = db.Column(db.Integer, default=20)
    seed = db.Column(db.Integer, nullable=True)
    model = db.Column(db.String(50), default='sdxl')  # 'sdxl' or 'flux'
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Style {self.name}>'


class ChatMessage(db.Model):
    """ChatMessage model for AI conversation history"""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChatMessage {self.role}: {self.content[:50]}...>'


class GeneratedImage(db.Model):
    """GeneratedImage model for storing generated image metadata"""
    __tablename__ = 'generated_images'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    thumbnail_path = db.Column(db.String(255), nullable=True)
    prompt = db.Column(db.Text, nullable=False)
    negative_prompt = db.Column(db.Text, nullable=True)
    style_id = db.Column(db.Integer, db.ForeignKey('styles.id'), nullable=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=True)
    model = db.Column(db.String(50), nullable=True)  # SDXL, Flux, SD, etc.
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    num_steps = db.Column(db.Integer, nullable=True)
    guidance_scale = db.Column(db.Float, nullable=True)
    seed = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    style = db.relationship('Style', backref='generated_images')
    theme = db.relationship('Theme', backref='generated_images')

    def __repr__(self):
        return f'<GeneratedImage {self.id}>'


class GenerativeModel(db.Model):
    """GenerativeModel model for storing AI image generation model configurations"""
    __tablename__ = 'generative_models'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # e.g., 'sdxl', 'flux'
    display_name = db.Column(db.String(100), nullable=False)  # e.g., 'SDXL (Stable Diffusion XL)'
    api_url = db.Column(db.String(255), nullable=False)  # e.g., 'https://gateway.pixazo.ai/getImage/v1/getSDXLImage'
    api_key = db.Column(db.String(255), nullable=True)  # Optional: API key for this specific model
    default_width = db.Column(db.Integer, default=768)
    default_height = db.Column(db.Integer, default=1024)
    default_steps = db.Column(db.Integer, default=20)
    default_guidance_scale = db.Column(db.Float, default=8.0)
    max_width = db.Column(db.Integer, default=1536)
    max_height = db.Column(db.Integer, default=2048)
    min_steps = db.Column(db.Integer, default=10)
    max_steps = db.Column(db.Integer, default=50)
    min_guidance_scale = db.Column(db.Float, default=1.0)
    max_guidance_scale = db.Column(db.Float, default=20.0)
    is_active = db.Column(db.Boolean, default=True)  # Enable/disable model
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<GenerativeModel {self.name}>'


class SavedPrompt(db.Model):
    """SavedPrompt model for storing user's saved generation prompts"""
    __tablename__ = 'saved_prompts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)  # User-defined name for the prompt
    main_prompt = db.Column(db.Text, nullable=False)
    negative_prompt = db.Column(db.Text, nullable=True)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=True)
    style_id = db.Column(db.Integer, db.ForeignKey('styles.id'), nullable=True)
    model_id = db.Column(db.Integer, db.ForeignKey('generative_models.id'), nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    num_steps = db.Column(db.Integer, nullable=True)
    guidance_scale = db.Column(db.Float, nullable=True)
    seed = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='saved_prompts')
    workspace = db.relationship('Workspace', backref='saved_prompts')
    theme = db.relationship('Theme', backref='saved_prompts')
    style = db.relationship('Style', backref='saved_prompts')
    model = db.relationship('GenerativeModel', backref='saved_prompts')

    def __repr__(self):
        return f'<SavedPrompt {self.name}>'
