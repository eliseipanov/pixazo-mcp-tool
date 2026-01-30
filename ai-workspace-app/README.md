# AI Workspace Web Application

A modern, dark-themed web application for experimenting with text-to-image AI models (SDXL, SD, Flux, etc.) with human-in-the-loop prompt refinement, batch generation with macros, saved styles & themes, and workspace persistence.

## Project Structure

```
ai-workspace-app/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # SQLAlchemy database models
├── init_db.py             # Database initialization script
├── db/                    # SQLite database directory
│   └── workspace.db       # SQLite database file
├── static/                # Static files
│   ├── css/
│   │   └── custom.css    # Custom CSS overrides
│   └── img/              # Images directory
├── templates/             # Jinja2 templates
│   ├── base.html          # Base template with Bootstrap
│   ├── index.html         # Home page
│   ├── auth/             # Authentication templates
│   │   ├── login.html
│   │   └── register.html
│   ├── workspaces/        # Workspace CRUD templates
│   │   ├── list.html
│   │   ├── create.html
│   │   ├── view.html
│   │   └── edit.html
│   ├── themes/           # Theme CRUD templates
│   │   ├── list.html
│   │   ├── create.html
│   │   └── edit.html
│   └── styles/           # Style CRUD templates
│       ├── list.html
│       ├── create.html
│       └── edit.html
└── uploads/              # User uploads
    ├── images/           # Generated images
    └── thumbnails/       # Image thumbnails
```

## Setup Instructions

### 1. Install Dependencies

The application uses the virtual environment at `/var/www/pixazo/.venv/`. Dependencies are already installed in the main `requirements.txt`:

```bash
# From the project root
/var/www/pixazo/.venv/bin/pip install -r requirements.txt
```

### 2. Initialize Database

Run the initialization script to create the database and sample data:

```bash
/var/www/pixazo/.venv/bin/python ai-workspace-app/init_db.py
```

This will create:
- Database tables
- Test user (username: `testuser`, password: `testpass123`)
- Sample themes (Photorealistic, Digital Art, Anime Style)
- Sample workspace with style and chat messages

### 3. Run the Application

```bash
/var/www/pixazo/.venv/bin/python ai-workspace-app/app.py
```

The application will be available at `http://127.0.0.1:5000/`

## Features

### Authentication
- User registration and login
- Password hashing with Werkzeug
- Session management with Flask-Login

### Workspaces
- Create, view, edit, and delete workspaces
- Organize AI generation sessions
- Track generated images per workspace

### Themes
- Define base prompts for consistent styles
- Create reusable prompt templates
- Share themes across workspaces

### Styles
- Configure generation parameters:
  - Positive and negative prompts
  - CFG scale (1-20)
  - Steps (1-150)
  - Seed for reproducibility
- Multiple styles per workspace

### Chat Messages
- AI chat history per workspace
- Context-aware conversations
- Role-based messages (user, assistant, system)

## Database Models

### User
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp
- `is_active`: Account status

### Workspace
- `id`: Primary key
- `name`: Workspace name
- `description`: Optional description
- `user_id`: Foreign key to User
- `theme_id`: Foreign key to Theme (optional)
- `created_at`, `updated_at`: Timestamps

### Theme
- `id`: Primary key
- `name`: Theme name
- `base_prompt`: Base prompt text
- `description`: Optional description
- `created_at`: Creation timestamp

### Style
- `id`: Primary key
- `name`: Style name
- `positive_prompt`: Positive prompt text
- `negative_prompt`: Negative prompt text
- `cfg_scale`: CFG scale value
- `steps`: Number of steps
- `seed`: Optional seed value
- `workspace_id`: Foreign key to Workspace
- `created_at`: Creation timestamp

### ChatMessage
- `id`: Primary key
- `workspace_id`: Foreign key to Workspace
- `role`: Message role (user/assistant/system)
- `content`: Message content
- `timestamp`: Message timestamp

### GeneratedImage
- `id`: Primary key
- `workspace_id`: Foreign key to Workspace
- `path`: Image file path
- `thumbnail_path`: Thumbnail file path
- `prompt`: Generation prompt
- `style_id`: Foreign key to Style (optional)
- `model`: Model name (SDXL, Flux, etc.)
- `created_at`: Creation timestamp

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Login form submission
- `GET /register` - Registration page
- `POST /register` - Registration form submission
- `GET /logout` - Logout

### Workspaces
- `GET /workspaces` - List workspaces (requires login)
- `GET /workspaces/create` - Create workspace form (requires login)
- `POST /workspaces/create` - Create workspace (requires login)
- `GET /workspaces/<id>` - View workspace (requires login)
- `GET /workspaces/<id>/edit` - Edit workspace form (requires login)
- `POST /workspaces/<id>/edit` - Update workspace (requires login)
- `POST /workspaces/<id>/delete` - Delete workspace (requires login)

### Themes
- `GET /themes` - List themes (requires login)
- `GET /themes/create` - Create theme form (requires login)
- `POST /themes/create` - Create theme (requires login)
- `GET /themes/<id>/edit` - Edit theme form (requires login)
- `POST /themes/<id>/edit` - Update theme (requires login)
- `POST /themes/<id>/delete` - Delete theme (requires login)

### Styles
- `GET /workspaces/<workspace_id>/styles` - List styles (requires login)
- `GET /workspaces/<workspace_id>/styles/create` - Create style form (requires login)
- `POST /workspaces/<workspace_id>/styles/create` - Create style (requires login)
- `GET /workspaces/<workspace_id>/styles/<style_id>/edit` - Edit style form (requires login)
- `POST /workspaces/<workspace_id>/styles/<style_id>/edit` - Update style (requires login)
- `POST /workspaces/<workspace_id>/styles/<style_id>/delete` - Delete style (requires login)

### Health Check
- `GET /api/health` - Health check endpoint

## Technology Stack

- **Backend**: Flask 3.x
- **Database**: SQLite (development)
- **ORM**: Flask-SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: Bootstrap 5.3 (dark theme)
- **Templating**: Jinja2
- **Password Hashing**: Werkzeug

## Development Roadmap

See [`ROADMAP_VARIANT_02.md`](ROADMAP_VARIANT_02.md) for the complete project roadmap including:

- Phase 3: Prompting, Analysis, Generation & Canvas
- Phase 4: Authentication, Plans & Monetization
- Phase 5: Polish, Export/Import, Security
- Phase 6: Dockerization & VPS Preparation

## Test Credentials

For quick testing, use the pre-configured test account:

- **Username**: `testuser`
- **Password**: `testpass123`

## Troubleshooting

If you experience issues with registration or login, see [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) for detailed troubleshooting steps.

### Quick Debug

Visit `/debug` endpoint to check your authentication status:
```
http://127.0.0.1:5000/debug
```

This will show:
- Whether you're authenticated
- Your user ID and username (if logged in)
- Total number of users in database

### Verify Database

Run the database test script:
```bash
/var/www/pixazo/.venv/bin/python ai-workspace-app/test_db.py
```

This will verify the database is working and list all users.

## Notes

- The application uses the virtual environment at `/var/www/pixazo/.venv/`
- Database is stored in `ai-workspace-app/db/workspace.db`
- Upload directories are automatically created on first run
- All routes except `/`, `/login`, `/register`, and `/api/health` require authentication
