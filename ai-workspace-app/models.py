# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and workspace ownership"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    workspaces = db.relationship('Workspace', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Workspace(db.Model):
    """Workspace model for organizing AI generation sessions"""
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
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
    style_id = db.Column(db.Integer, db.ForeignKey('styles.id'), nullable=True)
    model = db.Column(db.String(50), nullable=True)  # SDXL, Flux, SD, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    style = db.relationship('Style', backref='generated_images')

    def __repr__(self):
        return f'<GeneratedImage {self.id}>'
