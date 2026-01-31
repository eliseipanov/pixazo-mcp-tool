# app.py
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY, GROK_API_URL, GROK_API_KEY
from models import db, User, Workspace, Theme, Style, ChatMessage, GeneratedImage, GenerativeModel, SavedPrompt, generate_slug
from api_client import GrokAPIClient, build_generation_prompt
from image_utils import create_thumbnail, get_thumbnail_path
import logging
import os
import requests
import uuid
import json

# Configure logging to file
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'ai-workspace-app.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create database tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """Main page - show workspaces or redirect to create first workspace"""
    workspaces = Workspace.query.order_by(Workspace.updated_at.desc()).all()
    return render_template('index.html', workspaces=workspaces)


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok'}, 200


@app.route('/data/generated/<path:filename>')
@login_required
def serve_generated_image(filename):
    """Serve generated images from /var/www/pixazo/data/generated/ directory"""
    # Extract username and workspace from the path
    # The path format is: /data/generated/[username]/[workspacename]/filename
    # But the route only captures the part after /data/generated/
    # So we need to split the path to get username and workspace
    
    # The filename parameter contains the full path after /data/generated/
    # e.g., "username/workspacename/gen_abc123.png"
    path_parts = filename.split('/')
    
    if len(path_parts) < 3:
        return "Invalid path", 400
    
    username = path_parts[0]
    workspacename = path_parts[1]
    image_filename = '/'.join(path_parts[2:])
    
    # Check if the user has access to this image
    if current_user.username != username:
        return "Access denied", 403
    
    # Build the full path
    full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'generated', username, workspacename)
    
    return send_from_directory(full_path, image_filename)


@app.route('/data/generated/<path:filename>/thumbnail')
@login_required
def serve_thumbnail(filename):
    """Serve thumbnail images from /var/www/pixazo/data/generated/ directory"""
    # Extract username and workspace from path
    path_parts = filename.split('/')
    
    if len(path_parts) < 3:
        return "Invalid path", 400
    
    username = path_parts[0]
    workspacename = path_parts[1]
    image_filename = '/'.join(path_parts[2:])
    
    # Check if user has access to this image
    if current_user.username != username:
        return "Access denied", 403
    
    # Build full path
    full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'generated', username, workspacename)
    
    return send_from_directory(full_path, image_filename)


@app.route('/debug')
def debug():
    """Debug route to check authentication status"""
    return {
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.get_id() if current_user.is_authenticated else None,
        'username': current_user.username if current_user.is_authenticated else None,
        'user_count': User.query.count()
    }


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('register'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
            return redirect(url_for('register'))
    
    return render_template('auth/register.html')


@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


# Workspace routes
@app.route('/workspaces')
@login_required
def list_workspaces():
    """List all workspaces"""
    workspaces = Workspace.query.filter_by(user_id=current_user.id).order_by(Workspace.updated_at.desc()).all()
    return render_template('workspaces/list.html', workspaces=workspaces)


@app.route('/workspaces/create', methods=['GET', 'POST'])
@login_required
def create_workspace():
    """Create a new workspace"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Workspace name is required', 'danger')
            return redirect(url_for('create_workspace'))
        
        # Generate URL-safe slug from workspace name
        slug = generate_slug(name)
        
        # Check if slug already exists for this user
        existing = Workspace.query.filter_by(user_id=current_user.id, slug=slug).first()
        if existing:
            # Append a number to make it unique
            counter = 1
            while Workspace.query.filter_by(user_id=current_user.id, slug=f"{slug}-{counter}").first():
                counter += 1
            slug = f"{slug}-{counter}"
        
        workspace = Workspace(name=name, slug=slug, description=description, user_id=current_user.id)
        db.session.add(workspace)
        db.session.commit()
        
        flash(f'Workspace "{name}" created successfully', 'success')
        return redirect(url_for('view_workspace', workspace_id=workspace.id))
    
    return render_template('workspaces/create.html')


@app.route('/workspaces/<int:workspace_id>')
@login_required
def view_workspace(workspace_id):
    """View a specific workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('list_workspaces'))
    
    # Get all themes for the dropdown
    themes = Theme.query.order_by(Theme.name).all()
    
    return render_template('workspaces/view.html', workspace=workspace, themes=themes)


@app.route('/workspaces/<int:workspace_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workspace(workspace_id):
    """Edit a workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('list_workspaces'))
    
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_description = request.form.get('description')
        
        # Update name and description
        workspace.name = new_name
        workspace.description = new_description
        
        # Regenerate slug if name changed
        if new_name != workspace.name:
            new_slug = generate_slug(new_name)
            # Check if new slug already exists for this user (excluding current workspace)
            existing = Workspace.query.filter(
                Workspace.user_id == current_user.id,
                Workspace.slug == new_slug,
                Workspace.id != workspace.id
            ).first()
            if existing:
                # Append a number to make it unique
                counter = 1
                while Workspace.query.filter(
                    Workspace.user_id == current_user.id,
                    Workspace.slug == f"{new_slug}-{counter}",
                    Workspace.id != workspace.id
                ).first():
                    counter += 1
                new_slug = f"{new_slug}-{counter}"
            workspace.slug = new_slug
        
        workspace.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Workspace updated successfully', 'success')
        return redirect(url_for('view_workspace', workspace_id=workspace.id))
    
    return render_template('workspaces/edit.html', workspace=workspace)


@app.route('/workspaces/<int:workspace_id>/delete', methods=['POST'])
@login_required
def delete_workspace(workspace_id):
    """Delete a workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('list_workspaces'))
    
    db.session.delete(workspace)
    db.session.commit()
    flash('Workspace deleted successfully', 'success')
    return redirect(url_for('list_workspaces'))


# Theme routes
@app.route('/themes')
@login_required
def list_themes():
    """List all themes"""
    themes = Theme.query.order_by(Theme.created_at.desc()).all()
    return render_template('themes/list.html', themes=themes)


@app.route('/themes/create', methods=['GET', 'POST'])
@login_required
def create_theme():
    """Create a new theme"""
    if request.method == 'POST':
        name = request.form.get('name')
        base_prompt = request.form.get('base_prompt')
        description = request.form.get('description')
        
        if not name or not base_prompt:
            flash('Name and base prompt are required', 'danger')
            return redirect(url_for('create_theme'))
        
        theme = Theme(name=name, base_prompt=base_prompt, description=description)
        db.session.add(theme)
        db.session.commit()
        
        flash(f'Theme "{name}" created successfully', 'success')
        return redirect(url_for('list_themes'))
    
    return render_template('themes/create.html')


@app.route('/themes/<int:theme_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_theme(theme_id):
    """Edit a theme"""
    theme = Theme.query.get_or_404(theme_id)
    
    if request.method == 'POST':
        theme.name = request.form.get('name')
        theme.base_prompt = request.form.get('base_prompt')
        theme.description = request.form.get('description')
        
        db.session.commit()
        flash('Theme updated successfully', 'success')
        return redirect(url_for('list_themes'))
    
    return render_template('themes/edit.html', theme=theme)


@app.route('/themes/<int:theme_id>/delete', methods=['POST'])
@login_required
def delete_theme(theme_id):
    """Delete a theme"""
    theme = Theme.query.get_or_404(theme_id)
    db.session.delete(theme)
    db.session.commit()
    flash('Theme deleted successfully', 'success')
    return redirect(url_for('list_themes'))


# Style routes
@app.route('/workspaces/<int:workspace_id>/styles')
@login_required
def list_styles(workspace_id):
    """List styles for a workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('list_workspaces'))
    
    return render_template('styles/list.html', workspace=workspace, styles=workspace.styles)


@app.route('/workspaces/<int:workspace_id>/styles/create', methods=['GET', 'POST'])
@login_required
def create_style(workspace_id):
    """Create a new style for a workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('list_workspaces'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        positive_prompt = request.form.get('positive_prompt')
        negative_prompt = request.form.get('negative_prompt')
        cfg_scale = float(request.form.get('cfg_scale', 7.0))
        steps = int(request.form.get('steps', 20))
        seed = request.form.get('seed')
        model = request.form.get('model', 'sdxl')  # Default to SDXL
        
        if not name or not positive_prompt:
            flash('Name and positive prompt are required', 'danger')
            return redirect(url_for('create_style', workspace_id=workspace_id))
        
        style = Style(
            name=name,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            cfg_scale=cfg_scale,
            steps=steps,
            seed=int(seed) if seed else None,
            model=model,
            workspace_id=workspace_id
        )
        db.session.add(style)
        db.session.commit()
        
        flash(f'Style "{name}" created successfully', 'success')
        return redirect(url_for('list_styles', workspace_id=workspace_id))
    
    return render_template('styles/create.html', workspace=workspace)


@app.route('/workspaces/<int:workspace_id>/styles/<int:style_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_style(workspace_id, style_id):
    """Edit a style"""
    workspace = Workspace.query.get_or_404(workspace_id)
    style = Style.query.get_or_404(style_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('list_workspaces'))
    
    if request.method == 'POST':
        style.name = request.form.get('name')
        style.positive_prompt = request.form.get('positive_prompt')
        style.negative_prompt = request.form.get('negative_prompt')
        style.cfg_scale = float(request.form.get('cfg_scale', 7.0))
        style.steps = int(request.form.get('steps', 20))
        seed = request.form.get('seed')
        model = request.form.get('model', 'sdxl')
        style.seed = int(seed) if seed else None
        style.model = model
        
        db.session.commit()
        flash('Style updated successfully', 'success')
        return redirect(url_for('list_styles', workspace_id=workspace_id))
    
    return render_template('styles/edit.html', workspace=workspace, style=style)


@app.route('/workspaces/<int:workspace_id>/styles/<int:style_id>/delete', methods=['POST'])
@login_required
def delete_style(workspace_id, style_id):
    """Delete a style"""
    workspace = Workspace.query.get_or_404(workspace_id)
    style = Style.query.get_or_404(style_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('list_workspaces'))
    
    db.session.delete(style)
    db.session.commit()
    flash('Style deleted successfully', 'success')
    return redirect(url_for('list_styles', workspace_id=workspace_id))


# Image Generation routes

def download_image(image_url: str, save_path: str) -> bool:
    """
    Download image from remote URL and save locally.
    
    Args:
        image_url: URL of the image to download
        save_path: Local path to save the image
    
    Returns:
        True if download successful, False otherwise
    """
    try:
        logger.info(f"Downloading image from {image_url} to {save_path}")
        response = requests.get(image_url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        logger.info(f"Image downloaded successfully: {save_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return False


@app.route('/api/workspaces/<int:workspace_id>/generate', methods=['POST'])
@login_required
def generate_image(workspace_id):
    """Generate an image for a workspace"""
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return jsonify({'error': 'Workspace not found'}), 404
    
    # Check ownership
    if workspace.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get form data
        main_prompt = request.form.get('main_prompt', '').strip()
        theme_id = request.form.get('theme_id')
        style_id = request.form.get('style_id')
        model_id = request.form.get('model_id')
        negative_prompt_form = request.form.get('negative_prompt', '').strip()
        
        if not model_id:
            return jsonify({'error': 'Model is required'}), 400
        
        # Get model from database
        model = db.session.get(GenerativeModel, int(model_id))
        if not model or not model.is_active:
            return jsonify({'error': 'Invalid or inactive model'}), 400
        
        # Get optional parameters
        width = int(request.form.get('width', model.default_width))
        height = int(request.form.get('height', model.default_height))
        num_steps = int(request.form.get('num_steps', model.default_steps))
        guidance_scale = float(request.form.get('guidance_scale', model.default_guidance_scale))
        seed = request.form.get('seed')
        
        if not main_prompt:
            return jsonify({'error': 'Main prompt is required'}), 400
        
        # Get theme and style
        theme = None
        style = None
        theme_prompt = ''
        style_prompt = ''
        negative_prompt = negative_prompt_form  # Start with form negative prompt
        
        if theme_id:
            theme = db.session.get(Theme, int(theme_id))
            if theme:
                theme_prompt = theme.base_prompt
        
        if style_id:
            style = db.session.get(Style, int(style_id))
            if style:
                style_prompt = style.positive_prompt
                # Use style negative prompt if form negative prompt is empty
                if not negative_prompt and style.negative_prompt:
                    negative_prompt = style.negative_prompt
                # Use style parameters if not explicitly provided
                if not request.form.get('num_steps'):
                    num_steps = style.steps
                if not request.form.get('guidance_scale'):
                    guidance_scale = style.cfg_scale
                if not request.form.get('seed'):
                    seed = style.seed
        
        # Build final prompt
        final_prompt = build_generation_prompt(theme_prompt, main_prompt, style_prompt)
        
        # Initialize API client
        client = GrokAPIClient(base_url=GROK_API_URL, api_key=GROK_API_KEY)
        
        # Log all generation parameters
        logger.info(f"=== Image Generation Request ===")
        logger.info(f"Workspace ID: {workspace_id}, Name: {workspace.name}")
        logger.info(f"Model: {model.name} (ID: {model.id})")
        logger.info(f"Theme: {theme.name if theme else 'None'}")
        logger.info(f"Style: {style.name if style else 'None'}")
        logger.info(f"Main prompt: {main_prompt}")
        logger.info(f"Theme prompt: {theme_prompt}")
        logger.info(f"Style prompt: {style_prompt}")
        logger.info(f"Negative prompt: {negative_prompt}")
        logger.info(f"Final prompt: {final_prompt}")
        logger.info(f"Width: {width}, Height: {height}")
        logger.info(f"Steps: {num_steps}, CFG: {guidance_scale}")
        logger.info(f"Seed: {seed}")
        logger.info(f"==============================")
        
        # Generate image using Grok-Api server
        logger.info(f"Generating image with model: {model.name}, prompt: {final_prompt[:100]}...")
        result = client.generate_image_via_api_server(
            model=model.name,
            prompt=final_prompt,
            negative_prompt=negative_prompt if negative_prompt else None,
            width=width,
            height=height,
            num_steps=num_steps,
            guidance_scale=guidance_scale,
            seed=int(seed) if seed else -1,
            pixazo_api_key=model.api_key,
            request_template=model.request_template,
            response_template=model.response_template
        )
        
        if result.get('status') != 'success':
            return jsonify({'error': 'Image generation failed'}), 500
        
        # Download and save image locally
        image_url = result['image_url']
        # Store in /var/www/pixazo/data/generated/[username]/[workspace-slug]
        workspace_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'generated', current_user.username, workspace.slug)
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"gen_{uuid.uuid4().hex[:16]}.png"
        local_path = os.path.join(workspace_dir, filename)
        thumbnail_path = None
        
        # Download image
        if not download_image(image_url, local_path):
            logger.warning(f"Failed to download image, using remote URL: {image_url}")
            local_path = image_url  # Fallback to remote URL
        else:
            # Create thumbnail
            thumbnail_path = get_thumbnail_path(local_path)
            create_thumbnail(local_path, thumbnail_path)
        
        # Save generated image to database
        generated_image = GeneratedImage(
            workspace_id=workspace_id,
            path=local_path,
            thumbnail_path=thumbnail_path if thumbnail_path and os.path.exists(thumbnail_path) else None,
            prompt=final_prompt,
            negative_prompt=negative_prompt,
            model=model.name,
            width=width,
            height=height,
            num_steps=num_steps,
            guidance_scale=guidance_scale,
            seed=int(seed) if seed else None,
            theme_id=int(theme_id) if theme_id else None,
            style_id=int(style_id) if style_id else None
        )
        
        db.session.add(generated_image)
        
        # Update workspace timestamp
        workspace.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Image generated successfully: {local_path}")
        
        return jsonify({
            'status': 'success',
            'image_url': local_path,
            'image_id': generated_image.id,
            'parameters': result['parameters']
        })
        
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/workspaces/<int:workspace_id>/images')
@login_required
def get_workspace_images(workspace_id):
    """Get all generated images for a workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    images = GeneratedImage.query.filter_by(workspace_id=workspace_id).order_by(
        GeneratedImage.created_at.desc()
    ).all()
    
    return jsonify({
        'images': [{
            'id': img.id,
            'image_url': img.image_url,
            'prompt': img.prompt,
            'model': img.model,
            'width': img.width,
            'height': img.height,
            'created_at': img.created_at.isoformat() if img.created_at else None
        } for img in images]
    })


@app.route('/api/models')
@login_required
def get_models():
    """Get available image generation models"""
    models = GenerativeModel.query.filter_by(is_active=True).order_by(GenerativeModel.name).all()
    return jsonify({
        'models': [
            {
                'id': model.id,
                'name': model.name,
                'display_name': model.display_name,
                'default_width': model.default_width,
                'default_height': model.default_height,
                'default_steps': model.default_steps,
                'default_guidance_scale': model.default_guidance_scale,
                'max_width': model.max_width,
                'max_height': model.max_height,
                'min_steps': model.min_steps,
                'max_steps': model.max_steps,
                'min_guidance_scale': model.min_guidance_scale,
                'max_guidance_scale': model.max_guidance_scale
            }
            for model in models
        ]
    })


# Saved Prompts API Routes
@app.route('/api/workspaces/<int:workspace_id>/saved-prompts', methods=['GET'])
@login_required
def get_saved_prompts(workspace_id):
    """Get 10 latest saved prompts for a workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get 10 latest saved prompts for this workspace
    saved_prompts = SavedPrompt.query.filter_by(
        user_id=current_user.id,
        workspace_id=workspace_id
    ).order_by(SavedPrompt.created_at.desc()).limit(10).all()
    
    return jsonify({
        'saved_prompts': [
            {
                'id': sp.id,
                'name': sp.name,
                'main_prompt': sp.main_prompt,
                'negative_prompt': sp.negative_prompt,
                'theme_id': sp.theme_id,
                'style_id': sp.style_id,
                'model_id': sp.model_id,
                'width': sp.width,
                'height': sp.height,
                'num_steps': sp.num_steps,
                'guidance_scale': sp.guidance_scale,
                'seed': sp.seed,
                'created_at': sp.created_at.isoformat() if sp.created_at else None
            }
            for sp in saved_prompts
        ]
    })


@app.route('/api/workspaces/<int:workspace_id>/saved-prompts', methods=['POST'])
@login_required
def save_prompt(workspace_id):
    """Save a prompt for reuse"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Get form data
        name = data.get('name', 'Untitled')
        main_prompt = data.get('main_prompt')
        negative_prompt = data.get('negative_prompt')
        theme_id = data.get('theme_id')
        style_id = data.get('style_id')
        model_id = data.get('model_id')
        width = data.get('width')
        height = data.get('height')
        num_steps = data.get('num_steps')
        guidance_scale = data.get('guidance_scale')
        seed = data.get('seed')
        
        if not main_prompt:
            return jsonify({'error': 'Main prompt is required'}), 400
        
        # Create saved prompt
        saved_prompt = SavedPrompt(
            user_id=current_user.id,
            workspace_id=workspace_id,
            name=name,
            main_prompt=main_prompt,
            negative_prompt=negative_prompt,
            theme_id=int(theme_id) if theme_id else None,
            style_id=int(style_id) if style_id else None,
            model_id=int(model_id) if model_id else None,
            width=int(width) if width else None,
            height=int(height) if height else None,
            num_steps=int(num_steps) if num_steps else None,
            guidance_scale=float(guidance_scale) if guidance_scale else None,
            seed=int(seed) if seed else None
        )
        
        db.session.add(saved_prompt)
        db.session.commit()
        
        logger.info(f"Saved prompt '{name}' for workspace {workspace_id}")
        
        return jsonify({
            'status': 'success',
            'saved_prompt_id': saved_prompt.id
        })
    except Exception as e:
        logger.error(f"Error saving prompt: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/saved-prompts/<int:saved_prompt_id>', methods=['DELETE'])
@login_required
def delete_saved_prompt(saved_prompt_id):
    """Delete a saved prompt"""
    saved_prompt = SavedPrompt.query.get_or_404(saved_prompt_id)
    
    # Check ownership
    if saved_prompt.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(saved_prompt)
    db.session.commit()
    
    logger.info(f"Deleted saved prompt {saved_prompt_id}")
    
    return jsonify({'status': 'success'})


# Model Management Routes (Superuser only)
@app.route('/models')
@login_required
def list_models():
    """List all models (superuser only)"""
    if not current_user.is_superuser:
        flash('Access denied. Superuser only.', 'danger')
        return redirect(url_for('index'))
    
    models = GenerativeModel.query.order_by(GenerativeModel.name).all()
    return render_template('models/list.html', models=models)


@app.route('/models/create', methods=['GET', 'POST'])
@login_required
def create_model():
    """Create a new model (superuser only)"""
    if not current_user.is_superuser:
        flash('Access denied. Superuser only.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        api_url = request.form.get('api_url')
        api_key = request.form.get('api_key')
        default_width = int(request.form.get('default_width', 768))
        default_height = int(request.form.get('default_height', 1024))
        default_steps = int(request.form.get('default_steps', 20))
        default_guidance_scale = float(request.form.get('default_guidance_scale', 8.0))
        max_width = int(request.form.get('max_width', 1536))
        max_height = int(request.form.get('max_height', 2048))
        min_steps = int(request.form.get('min_steps', 10))
        max_steps = int(request.form.get('max_steps', 50))
        min_guidance_scale = float(request.form.get('min_guidance_scale', 1.0))
        max_guidance_scale = float(request.form.get('max_guidance_scale', 20.0))
        
        if not name or not display_name or not api_url:
            flash('Name, display name, and API URL are required', 'danger')
            return redirect(url_for('create_model'))
        
        model = GenerativeModel(
            name=name,
            display_name=display_name,
            api_url=api_url,
            api_key=api_key,
            default_width=default_width,
            default_height=default_height,
            default_steps=default_steps,
            default_guidance_scale=default_guidance_scale,
            max_width=max_width,
            max_height=max_height,
            min_steps=min_steps,
            max_steps=max_steps,
            min_guidance_scale=min_guidance_scale,
            max_guidance_scale=max_guidance_scale
        )
        
        try:
            db.session.add(model)
            db.session.commit()
            flash(f'Model "{display_name}" created successfully', 'success')
            return redirect(url_for('list_models'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating model: {str(e)}', 'danger')
            return redirect(url_for('create_model'))
    
    return render_template('models/create.html')


@app.route('/models/<int:model_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_model(model_id):
    """Edit a model (superuser only)"""
    if not current_user.is_superuser:
        flash('Access denied. Superuser only.', 'danger')
        return redirect(url_for('index'))
    
    model = db.session.get(GenerativeModel, model_id)
    if not model:
        flash('Model not found', 'danger')
        return redirect(url_for('list_models'))
    
    if request.method == 'POST':
        model.name = request.form.get('name')
        model.display_name = request.form.get('display_name')
        model.api_url = request.form.get('api_url')
        model.api_key = request.form.get('api_key')
        model.default_width = int(request.form.get('default_width', 768))
        model.default_height = int(request.form.get('default_height', 1024))
        model.default_steps = int(request.form.get('default_steps', 20))
        model.default_guidance_scale = float(request.form.get('default_guidance_scale', 8.0))
        model.max_width = int(request.form.get('max_width', 1536))
        model.max_height = int(request.form.get('max_height', 2048))
        model.min_steps = int(request.form.get('min_steps', 10))
        model.max_steps = int(request.form.get('max_steps', 50))
        model.min_guidance_scale = float(request.form.get('min_guidance_scale', 1.0))
        model.max_guidance_scale = float(request.form.get('max_guidance_scale', 20.0))
        model.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash(f'Model "{model.display_name}" updated successfully', 'success')
            return redirect(url_for('list_models'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating model: {str(e)}', 'danger')
            return redirect(url_for('edit_model', model_id=model_id))
    
    return render_template('models/edit.html', model=model)


@app.route('/models/<int:model_id>/delete', methods=['POST'])
@login_required
def delete_model(model_id):
    """Delete a model (superuser only)"""
    if not current_user.is_superuser:
        flash('Access denied. Superuser only.', 'danger')
        return redirect(url_for('index'))
    
    model = db.session.get(GenerativeModel, model_id)
    if not model:
        flash('Model not found', 'danger')
        return redirect(url_for('list_models'))
    
    try:
        db.session.delete(model)
        db.session.commit()
        flash(f'Model "{model.display_name}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting model: {str(e)}', 'danger')
    
    return redirect(url_for('list_models'))


@app.route('/api/workspaces/<int:workspace_id>/themes')
@login_required
def get_workspace_themes(workspace_id):
    """Get available themes for a workspace"""
    themes = Theme.query.order_by(Theme.name).all()
    return jsonify({
        'themes': [{
            'id': theme.id,
            'name': theme.name,
            'base_prompt': theme.base_prompt,
            'description': theme.description
        } for theme in themes]
    })


@app.route('/api/workspaces/<int:workspace_id>/styles')
@login_required
def get_workspace_styles(workspace_id):
    """Get available styles for a workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Check ownership
    if workspace.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'styles': [{
            'id': style.id,
            'name': style.name,
            'positive_prompt': style.positive_prompt,
            'negative_prompt': style.negative_prompt,
            'model': style.model,
            'cfg_scale': style.cfg_scale,
            'steps': style.steps,
            'seed': style.seed
        } for style in workspace.styles]
    })


# Image Action API Routes
@app.route('/api/images/<int:image_id>', methods=['GET'])
@login_required
def get_image_info(image_id):
    """Get detailed information about a generated image"""
    image = GeneratedImage.query.get_or_404(image_id)
    
    # Check ownership
    workspace = Workspace.query.get(image.workspace_id)
    if not workspace or workspace.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'id': image.id,
        'path': image.path,
        'thumbnail_path': image.thumbnail_path,
        'prompt': image.prompt,
        'negative_prompt': image.negative_prompt,
        'model': image.model,
        'width': image.width,
        'height': image.height,
        'num_steps': image.num_steps,
        'guidance_scale': image.guidance_scale,
        'seed': image.seed,
        'theme_id': image.theme_id,
        'style_id': image.style_id,
        'created_at': image.created_at.isoformat() if image.created_at else None
    })


@app.route('/api/images/<int:image_id>', methods=['DELETE'])
@login_required
def delete_image(image_id):
    """Delete a generated image"""
    image = GeneratedImage.query.get_or_404(image_id)
    
    # Check ownership
    workspace = Workspace.query.get(image.workspace_id)
    if not workspace or workspace.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Delete image file
        if image.path and os.path.exists(image.path):
            os.remove(image.path)
            logger.info(f"Deleted image file: {image.path}")
        
        # Delete thumbnail file
        if image.thumbnail_path and os.path.exists(image.thumbnail_path):
            os.remove(image.thumbnail_path)
            logger.info(f"Deleted thumbnail file: {image.thumbnail_path}")
        
        # Delete database record
        db.session.delete(image)
        db.session.commit()
        
        logger.info(f"Deleted image {image_id}")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Context processor for templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)