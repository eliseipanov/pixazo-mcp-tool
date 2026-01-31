# AI Image Generation Workspace App – Actual Project State

**Last Updated**: 2026-01-31

**Purpose**: This document captures the current state of the project for future developers and architects. It documents what has been completed, what is pending, and any known issues or deviations from the original roadmap.

---

## Project Overview

**Goal**: Build a modern, dark-themed web application for experimenting with text-to-image AI models (SDXL, Flux) with human-in-the-loop prompt refinement, saved styles & themes, workspace persistence, and export/import.

**Current Stack**:
- **Backend**: Flask 3.x + Flask-SQLAlchemy + Flask-Login
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5.3+ (dark theme) + Jinja2 + vanilla JS (Fetch API)
- **Image Processing**: Pillow (for thumbnails - pending)
- **API Server**: FastAPI (Grok-Api) as proxy to Pixazo API
- **External API**: Pixazo AI (SDXL, Flux Klein)

**Working Directory**: `/var/www/pixazo/ai-workspace-app/`
**Virtual Environment**: `/var/www/pixazo/.venv/bin/python`
**Database**: `/var/www/pixazo/ai-workspace-app/db/workspace.db`
**Image Storage**: `/var/www/pixazo/data/generated/[username]/[workspace-slug]/`
**Logs**: `/var/www/pixazo/logs/ai-workspace-app.log`

---

## Phase 1 – Planning & Skeleton

**Status**: ✅ Complete

### Completed Tasks
- Created project structure in `ai-workspace-app/`
- Set up Flask 3.x application with Bootstrap 5.3 dark theme
- Created base template with responsive layout
- Implemented basic routes: `/`, `/api/health`
- Set up logging to file

### Files Created
- `ai-workspace-app/app.py` - Main Flask application
- `ai-workspace-app/config.py` - Configuration
- `ai-workspace-app/templates/base.html` - Master template
- `ai-workspace-app/templates/index.html` - Landing page
- `ai-workspace-app/static/css/custom.css` - Custom styles

---

## Phase 2 – Workspaces, Themes, Styles

**Status**: ✅ Complete

### Completed Tasks
- Created SQLAlchemy models: User, Workspace, Theme, Style, ChatMessage, GeneratedImage
- Implemented CRUD routes for Workspaces, Themes, Styles
- Added workspace management UI
- Added theme and style management UI
- Implemented workspace-specific image storage
- Added URL-safe workspace names (slugs)

### Database Models
- **User**: id, username, email, password_hash, is_superuser, created_at
- **Workspace**: id, name, slug, owner_id, theme_id, created_at
- **Theme**: id, name, base_prompt, description, created_at
- **Style**: id, name, positive_prompt, negative_prompt, cfg_scale, steps, seed, workspace_id, model_id
- **ChatMessage**: id, workspace_id, role, content, timestamp
- **GeneratedImage**: id, workspace_id, path, thumbnail_path, prompt, negative_prompt, style_id, model_id, width, height, num_steps, guidance_scale, seed, created_at
- **SavedPrompt**: id, workspace_id, name, main_prompt, negative_prompt, theme_id, style_id, model_id, width, height, num_steps, guidance_scale, seed, created_at
- **GenerativeModel**: id, name, model_type, api_url, api_key, is_active, created_at

### Files Created/Modified
- `ai-workspace-app/models.py` - SQLAlchemy models
- `ai-workspace-app/templates/workspaces/` - Workspace templates
- `ai-workspace-app/templates/themes/` - Theme templates
- `ai-workspace-app/templates/styles/` - Style templates

### Database Migrations
- `migrate_add_slug.py` - Added slug column to workspaces table
- `migrate_saved_prompts.py` - Created saved_prompts table

---

## Phase 3 – Image Generation Integration

**Status**: ✅ Complete

### Completed Tasks
- Created API client for communicating with Grok-Api server
- Integrated image generation into workspace view
- Added image download and storage to workspace folders
- Implemented database-driven model configuration
- Added superuser support for model management
- Added Negative Prompt field to generation form
- Added saved prompts feature with save/load functionality

### API Endpoints (Grok-Api Server)
- `POST /v1/generate/sdxl` - Generate SDXL image
- `POST /v1/generate/flux` - Generate Flux Klein image
- `POST /v1/chat/completions` - Chat completions (for prompt improvement)

### API Endpoints (Web App)
- `POST /workspaces/<workspace_id>/generate` - Generate image
- `GET /api/workspaces/<workspace_id>/saved-prompts` - Get saved prompts
- `POST /api/workspaces/<workspace_id>/saved-prompts` - Save prompt
- `DELETE /api/saved-prompts/<saved_prompt_id>` - Delete saved prompt
- `GET /generated/<path:filepath>` - Serve generated images

### Files Created/Modified
- `ai-workspace-app/api_client.py` - API client for Grok-Api server
- `Grok-Api/api_server.py` - FastAPI server with image generation endpoints
- `ai-workspace-app/templates/workspaces/view.html` - Workspace view with generation form

### Known Issues & Fixes
1. **HTTP 422 Validation Error** - Fixed by ensuring seed is always an integer (never None)
2. **HTTP 500 "PIXAZO_API_KEY not configured"** - Fixed by accepting API key from request payload
3. **Permission denied for /data directory** - Fixed by using `/var/www/pixazo/data/` instead of `/data/`
4. **Spaces in workspace names** - Fixed by adding slug field to Workspace model
5. **Saved prompts not appearing in dropdown** - Fixed by ensuring save completes before page reload

---

## Phase 4 – Authentication, Plans & Monetization

**Status**: ⏳ Pending

### Pending Tasks
- Implement user registration and login
- Add password reset functionality
- Implement plan enforcement (Free vs All Inclusive)
- Add Redis for rate limiting and daily generation limits
- Integrate Stripe for payments
- Create admin panel with Flask-Admin
- Add helpdesk ticket form

---

## Phase 5 – Polish, Export/Import, Security

**Status**: ⏳ Pending

### Pending Tasks
- Add input sanitization and rate limiting (Flask-Limiter)
- Implement error handling and user-friendly toasts/modals
- Create workspace export/import (.GZ archive)
- Add accessibility basics (ARIA labels)
- Ensure dark theme consistency
- Add basic SEO meta tags

---

## Phase 6 – Dockerization & VPS Preparation

**Status**: ⏳ Pending

### Pending Tasks
- Create Dockerfile (python:3.12-slim base)
- Create docker-compose.yml with app, db, redis, celery-worker, nginx
- Test locally with docker-compose
- Prepare deployment checklist
- Set up VPS (Ubuntu, Docker, ufw, fail2ban)
- Configure domain and Let's Encrypt
- Set up persistent volumes

---

## Additional Features Implemented

### Saved Prompts Feature
- Users can save generation prompts with all parameters
- Saved prompts appear in dropdown for quick loading
- Supports saving: main prompt, negative prompt, theme, style, model, dimensions, steps, guidance scale, seed
- API endpoints for CRUD operations on saved prompts

### UI/UX Redesign (2026-01-31)
- **Status**: ✅ Complete

#### Completed Tasks
- Redesigned workspace view with new layout
- Added resizable sidebar (320px-420px) with resize handle
- Added collapsible navigation menu with header and state saving
- Moved prompt form to sidebar (always visible)
- Moved workspace actions (Edit, Save, Export, Import, Delete) to navbar
- Moved chat toggle button to navbar (icon-only, changes color on toggle)
- Expanded main canvas area for generated images grid
- Created floating chat window component
- Implemented drag-and-drop for chat window
- Implemented resize functionality for chat window (with min/max limits)
- Added collapse/expand functionality for chat window
- Implemented chat toggle button behavior
- Saved chat window position, size, and state in localStorage
- Saved sidebar width and nav menu state in localStorage
- Added smooth transitions and animations

#### Layout Structure
- **Navbar**:
  - Logo/brand link to Home
  - Workspace Actions (Edit, Save, Export, Import, Delete) - icon buttons
  - Chat Toggle Button - icon button (blue when off, green when on)
  - Navigation links (Home, Workspaces, Themes, Models)
  - User dropdown with Logout option
- **Left Sidebar (Resizable: 320px-420px)**:
  - Navigation Menu (Collapsible with header, state saved)
  - Prompt Form (Always visible)
- **Main Canvas Area (Full width)**:
  - Generated Images Grid
  - Empty state with "Generate your first image" message
- **Floating Chat Window (when toggle is ON)**:
  - Draggable by header
  - Collapsible to header only
  - Resizable (with min/max limits)
  - Close button
  - Chat messages (scrollable)
  - Input field and Send button
  - Position saved in localStorage
  - First open: Centered on screen
  - Subsequent opens: At last saved position

#### localStorage Keys
- `chatWindow_position`: {x, y}
- `chatWindow_size`: {width, height}
- `chatWindow_collapsed`: boolean
- `chatWindow_visible`: boolean
- `sidebar_width`: number (320-420)
- `navMenu_collapsed`: boolean

#### Constraints
- **Sidebar**:
  - Min width: 320px
  - Max width: 420px
  - Default width: 320px
  - State saved in localStorage
- **Chat Window**:
  - Min width: 300px
  - Min height: 200px
  - Max width: 600px
  - Max height: 800px
  - Default size: 400x500px
  - Default position: Centered on first open
  - Subsequent position: Last saved position
  - Collapsed state: Header only (height ~40px)

#### Files Modified
- `ai-workspace-app/templates/base.html` - Added navbar with workspace_actions block
- `ai-workspace-app/templates/workspaces/view.html` - Complete redesign with new layout
- `ai-workspace-app/static/css/custom.css` - Added styles for navbar and workspace actions

### URL-Safe Workspace Names
- Workspace names with spaces are converted to slugs
- Slugs are used in file paths and URLs
- Ensures consistent file system paths

### Database-Driven Model Configuration
- Models are stored in database instead of config.py
- Superusers can manage models via admin panel
- Regular users can only select from available models
- API keys are stored per model in database

---

## Configuration Files

### ai-workspace-app/config.py
- Database URI: `sqlite:///db/workspace.db`
- Secret key for session management
- Upload folder configuration

### Grok-Api/.env
- PIXAZO_API_KEY: API key for Pixazo service
- GROK_API_KEY: API key for Grok service (for chat)

---

## Database Schema

### Tables
- `users` - User accounts
- `workspaces` - User workspaces with slugs
- `themes` - Base prompts for workspaces
- `styles` - Style presets for workspaces
- `chat_messages` - Chat history per workspace
- `generated_images` - Generated image metadata
- `saved_prompts` - User's saved generation prompts
- `generative_models` - Available AI models

### Current Database State
- SDXL model configured with API key
- Workspace "Single Portraits of Highest Quality" with slug "single-portraits-of-highest-quality"
- All generation parameters are saved to database for reuse

---

## Known Limitations

1. **No thumbnails yet** - Full-size images are displayed directly (thumbnails pending)
2. **No batch generation** - Only single image generation supported
3. **No prompt parser** - Macro expansion not implemented
4. **No chat integration** - Prompt improvement via chat not implemented
5. **No export/import** - Workspace backup/restore not implemented
6. **No authentication** - No user registration/login yet
7. **No rate limiting** - No daily generation limits
8. **SQLite only** - PostgreSQL not yet configured for production

---

## Next Steps

### Immediate Priorities
1. Test image generation flow end-to-end
2. Add thumbnails for generated images
3. Add full-size modal view with actions (Save, Delete, Retry)
4. Implement chat UI for prompt improvement

### Short-term Goals
1. Complete Phase 4 (Authentication & Monetization)
2. Complete Phase 5 (Polish & Export/Import)
3. Complete Phase 6 (Dockerization)

### Long-term Goals
1. Beta testing with early users
2. Add user-facing subscription page
3. Implement helpdesk ticketing system
4. Add analytics (popular models/styles)
5. Optional: WebSocket chat (Flask-SocketIO)
6. Optional: Multi-user shared workspaces

---

## Development Notes

### Running the Application
```bash
# Activate virtual environment
source /var/www/pixazo/.venv/bin/activate

# Run Flask app
cd /var/www/pixazo/ai-workspace-app
python app.py

# Run Grok-Api server (in separate terminal)
cd /var/www/pixazo/Grok-Api
uvicorn api_server:app --host 0.0.0.0 --port 6969 --workers 5
```

### Testing Image Generation
1. Create a workspace
2. Select a theme and style
3. Enter a prompt and click "Generate Image"
4. Image will be saved to `/var/www/pixazo/data/generated/[username]/[workspace-slug]/`
5. Check logs at `/var/www/pixazo/logs/ai-workspace-app.log`

### Adding New Models
1. Log in as superuser
2. Go to Admin panel
3. Add new GenerativeModel with name, type, API URL, and API key
4. Model will be available in generation form

---

## Contact & Support

For questions or issues, refer to:
- Original roadmap: `ai-workspace-app/ROADMAP_VARIANT_02.md`
- Phase 1 tasks: `ai-workspace-app/Tasks/phase_one_tasks.md`
- Project root: `/var/www/pixazo/`
