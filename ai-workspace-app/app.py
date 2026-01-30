# app.py
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY
from models import db, User, Workspace, Theme, Style, ChatMessage, GeneratedImage

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
        
        workspace = Workspace(name=name, description=description, user_id=current_user.id)
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
    
    return render_template('workspaces/view.html', workspace=workspace)


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
        workspace.name = request.form.get('name')
        workspace.description = request.form.get('description')
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


# Context processor for templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)