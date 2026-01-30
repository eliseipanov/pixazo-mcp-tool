# AI Image Generation Workspace App – Project Roadmap

**Goal**  
Build a modern, dark-themed web application for experimenting with text-to-image AI models (SDXL, SD, Flux, etc.) with human-in-the-loop prompt refinement, batch generation with macros, saved styles & themes, workspace persistence, export/import, and future monetization (Free + $8.99 All Inclusive plans).

**Target audience during development**  
- Architects (high-level structure)  
- Coders (implementation via Codestral / human)  
- LLM agents (Codestral, etc.) — simple, predictable stack

**Recommended Stack (2026 edition)**

- **Backend**            Flask 3.x + Flask-SQLAlchemy + Flask-Login + Flask-Admin + Celery  
- **Database**           SQLite (dev) → PostgreSQL (prod)  
- **Caching / Limits**   Redis  
- **Frontend**           Bootstrap 5.3+ (dark theme, desktop-first) + Jinja2 + vanilla JS (Fetch API)  
- **Styling extras**     Tailwind CSS (optional, for rapid overrides)  
- **Image processing**   Pillow (thumbnails)  
- **Async / Batch**      Celery + Redis  
- **Payments**           Stripe (webhooks)  
- **Export/Import**      tarfile + gzip (.GZ archives)  
- **Deployment**         Docker + docker-compose (single-container MVP → multi-service)  
- **Hosting target**     VPS (Ubuntu 24.04) with Docker, Nginx, Let's Encrypt

**Development Phases**

### Phase 1 – Planning & Skeleton (1–2 days)

- Create Git repository  
- Set up Python 3.12 venv + install core packages  
- Initialize minimal Flask app (`app.py`)  
- Add Bootstrap 5.3 dark theme via CDN  
- Basic layout:  
  - Left sidebar – Control Panel (chat placeholder)  
  - Right main area – Canvas / Tablet placeholder (dark matte texture)  
- Routes: `/` (main page), `/api/health`  
- Run `flask run` and verify dark Bootstrap layout renders correctly

**Deliverable**: running skeleton with desktop-first dark UI

### Phase 2 – Workspaces, Themes, Styles (7–14 days)

- SQLAlchemy models:  
  - User  
  - Workspace (name, owner, theme_id, created_at)  
  - Theme (name, base_prompt, description)  
  - Style (positive, negative, cfg_scale, steps, seed, workspace_id)  
  - ChatMessage (workspace_id, role, content, timestamp)  
  - GeneratedImage (workspace_id, path, thumbnail_path, prompt, style_id, created_at)  
- CRUD routes & forms for:  
  - Create / list / delete / rename Workspace  
  - Create / edit / delete Theme  
  - Create / edit / delete Style (positive / negative / params)  
- Workspace export / import (.GZ archive):  
  - JSON metadata + chat history + all images & thumbnails  
- Basic AI chat in sidebar:  
  - Send message → call LLM API (OpenAI / Mistral / Codestral)  
  - Persist messages per workspace  
  - System prompt includes current Theme context

**Deliverable**: user can create workspace, save themes & styles, chat remembers context

### Phase 3 – Prompting, Analysis, Generation & Canvas (5–10 days)

- Prompt parser & macro expander:  
  - Detect `{opt1|opt2|opt3}` syntax  
  - Calculate combinations (min 3 – optimal 6 generations)  
  - Show modal: "Generate batch of 6 images? Yes / No"  
- Generation route `/api/generate`:  
  - Accept model, prompt, style_id, batch_size  
  - Call existing image generation API (SDXL / Flux / etc.)  
  - Save original + thumbnail (Pillow 256×256 or similar)  
- Canvas ("Tablet") view:  
  - Dark matte background texture  
  - Responsive grid of generated image thumbnails  
  - Click → open full-size modal  
  - Buttons: Save to disk / Delete / Retry with same prompt  
- AJAX refresh after generation (poll or WebSocket lite via long-polling)

**Deliverable**: user can discuss prompt in chat, generate single or batch images, see results on canvas

### Phase 4 – Authentication, Plans & Monetization (5–8 days)

- Flask-Login integration  
- User registration / login / password reset  
- Plans:  
  - Free: max 20 gens/day, 1 workspace  
  - All Inclusive: unlimited (test with this plan first)  
- Redis counters for daily generation limit  
- Stripe integration:  
  - Checkout session creation  
  - Webhook handler for subscription events  
- Superuser (/admin):  
  - Flask-Admin interface  
  - List users, see payments, daily usage  
  - Helpdesk ticket form + email notifications (Flask-Mail)

**Deliverable**: authenticated users, plan enforcement, admin panel

### Phase 5 – Polish, Export/Import, Security (4–7 days)

- Input sanitization & rate limiting (Flask-Limiter)  
- Error handling & user-friendly toasts/modals  
- Full workspace export/import testing  
- Accessibility basics (ARIA labels on interactive elements)  
- Dark theme consistency check across components  
- Basic SEO meta tags on main page

**Deliverable**: production-ready UX feel, reliable backup/restore

### Phase 6 – Dockerization & VPS Preparation (3–6 days)

- Write `Dockerfile` (python:3.12-slim base)  
- Create `docker-compose.yml`:  
  - app (Flask)  
  - db (postgres)  
  - redis  
  - celery-worker  
  - nginx (static files + reverse proxy)  
- Local test: `docker-compose up`  
- Prepare deployment checklist:  
  - VPS setup (Ubuntu, Docker, ufw, fail2ban)  
  - Domain + Let's Encrypt  
  - Persistent volumes for images & database  
  - Environment variables (.env)  
- Push image to private registry or Docker Hub (optional)

**Deliverable**: fully containerized application ready for VPS deployment

**Total estimated time (1 dev + heavy Codestral usage)**: 4–8 weeks to MVP-ready state

**Next steps after MVP**  
- Beta testing (10–20 early users)  
- Add user-facing subscription page  
- Implement helpdesk ticketing system  
- Analytics (basic – which models/styles are popular)  
- Optional: WebSocket chat (via Flask-SocketIO)  
- Optional: multi-user shared workspaces

Good luck — this roadmap should give clear structure to architects, coders and LLM agents alike.


<xai:tool_usage_card>
  <xai:tool_usage_card_id>f22df46c-1a3b-4233-be9e-df322a9a1a4e</xai:tool_usage_card_id>
  <xai:tool_name>web_search</xai:tool_name>
  <xai:tool_args><![CDATA[{"query":"Bootstrap 5.3 dark theme desktop first landing page example 2026","num_results":5}]]></xai:tool_args>
</xai:tool_usage_card><xai:tool_usage_card>
  <xai:tool_usage_card_id>4ade0d3b-c972-4d6b-9873-88c00becc7cc</xai:tool_usage_card_id>
  <xai:tool_name>web_search</xai:tool_name>
  <xai:tool_args><![CDATA[{"query":"best practices Flask minimal app structure with Bootstrap dark mode 2026","num_results":5}]]></xai:tool_args>
</xai:tool_usage_card>Here is a **zoomed-in, detailed version of Phase 1** — structured so that architects, coders, and LLM agents (like Codestral in VSCode) can immediately start working from it. Everything is written in clear, copy-paste friendly English Markdown.

```markdown
# Phase 1 – Planning & Skeleton  
**Duration estimate**: 1–2 days (with heavy Codestral assistance)  
**Goal**: Create a minimal, running Flask application with a modern dark Bootstrap 5.3 layout (desktop-first priority), left sidebar (Control Panel placeholder), right canvas area (Tablet placeholder), and basic health-check route.

### Objectives
- Verify the stack works end-to-end locally  
- Establish clean project structure that Codestral can easily extend  
- Set up dark theme consistently (using Bootstrap native dark mode)  
- Keep client-side JavaScript to absolute minimum (only Bootstrap JS + Fetch for future AJAX)  
- Desktop-first: optimize for ≥1024 px screens; mobile responsiveness is secondary at this stage

### Recommended Folder Structure (minimal & predictable)
```
ai-workspace-app/
├── app.py                  # main Flask application
├── config.py               # configuration (or use .env later)
├── requirements.txt
├── static/
│   ├── css/
│   │   └── custom.css      # overrides & matte texture if needed
│   └── img/
│       └── matte-bg.jpg    # optional dark matte background texture (small file)
├── templates/
│   ├── base.html           # master template with Bootstrap + layout skeleton
│   └── index.html          # main landing / workspace view
└── .env                    # (git ignored) for secrets later
```

### Step-by-Step Tasks

1. **Initialize Project & Virtual Environment**
   - Create folder `ai-workspace-app`
   - Run:
     ```
     python -m venv venv
     source venv/bin/activate    # or venv\Scripts\activate on Windows
     pip install flask
     pip freeze > requirements.txt
     ```
   - (Later add more: `flask-sqlalchemy flask-login flask-admin requests pillow celery redis stripe flask-mail flask-limiter`)

2. **Create Basic app.py**
   ```python
   # app.py
   from flask import Flask, render_template

   app = Flask(__name__)
   app.config['SECRET_KEY'] = 'dev-secret-key-change-me'  # placeholder

   @app.route('/')
   def index():
       return render_template('index.html')

   @app.route('/api/health')
   def health():
       return {'status': 'ok'}, 200

   if __name__ == '__main__':
       app.run(debug=True)
   ```

3. **Add Bootstrap 5.3 via CDN + Dark Mode (templates/base.html)**
   ```html
   <!DOCTYPE html>
   <html lang="en" data-bs-theme="dark">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1">
       <title>AI Workspace – Experiment Lab</title>

       <!-- Bootstrap 5.3 CSS + Icons -->
       <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
       <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">

       <!-- Custom overrides -->
       <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
   </head>
   <body class="bg-dark text-light">
       <div class="d-flex min-vh-100">
           <!-- Left Sidebar – Control Panel -->
           <aside class="sidebar bg-dark border-end border-secondary p-3 d-flex flex-column" style="width: 320px;">
               <h4 class="text-center mb-4">Control Panel</h4>
               <div class="flex-grow-1">
                   <!-- Chat placeholder -->
                   <div class="card bg-secondary text-light p-3 mb-3">
                       <p class="text-muted">AI Chat will appear here…</p>
                   </div>
               </div>
               <div class="mt-auto text-center small text-muted">
                   Workspace: <strong>Untitled</strong>
               </div>
           </aside>

           <!-- Main Canvas / Tablet Area -->
           <main class="flex-grow-1 p-4 canvas-area">
               <h2 class="mb-4">Tablet / Canvas</h2>
               <div class="card bg-secondary-subtle text-light p-5 text-center" style="min-height: 70vh;">
                   <p class="lead text-muted">Generated images will appear here as thumbnails on a matte dark surface…</p>
               </div>
           </main>
       </div>

       <!-- Bootstrap JS (for collapse, modals, etc.) -->
       <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
   </body>
   </html>
   ```

4. **index.html extends base**
   ```html
   {% extends "base.html" %}

   {% block title %}AI Workspace – Home{% endblock %}

   {% block content %}
   <!-- Can override or add extra content here later -->
   {% endblock %}
   ```

5. **Minimal custom.css (static/css/custom.css)**
   ```css
   /* Matte dark texture simulation */
   .canvas-area {
       background: #0f0f0f url('../img/matte-bg.jpg') repeat;  /* optional small texture ~100×100 px */
       background-size: 200px;
   }

   .sidebar {
       border-right: 1px solid #333 !important;
   }

   /* Desktop-first: hide sidebar on <1024px for now (later responsive offcanvas) */
   @media (max-width: 1023px) {
       .sidebar {
           display: none;  /* temporary – will become offcanvas later */
       }
   }
   ```

6. **Run & Verify**
   - `flask run` or `python app.py`
   - Open http://127.0.0.1:5000/
   - Check:
     - Dark theme everywhere
     - Left fixed-width sidebar (~320 px)
     - Right flexible canvas area
     - No light elements leaking
     - Looks good on 1440p+ monitor
   - Bonus: open http://127.0.0.1:5000/api/health → should return JSON

### Codestral-friendly Prompts for Phase 1 Extensions
Paste these directly into your VSCode chat with Codestral:

1. **Extend base.html with placeholder for future chat input form**
   ```
   Add to base.html inside the sidebar card: a simple form with textarea for prompt, select for model (SDXL, Flux Klein, SD), button "Generate". Use Bootstrap form classes, no JS yet – just static HTML.
   ```

2. **Add offcanvas toggle for mobile (future-proof)**
   ```
   In base.html, add a navbar at top with button that opens the sidebar as Bootstrap offcanvas on screens <1024px. Keep sidebar visible by default on desktop.
   ```

3. **Create a matte texture background**
   ```
   Suggest CSS or generate a very small repeating dark matte texture description that I can create in 5 seconds in any image editor.
   ```

### Exit Criteria for Phase 1
- Flask app starts without errors  
- Page loads with dark Bootstrap theme  
- Layout: fixed left sidebar (Control Panel), flexible right canvas  
- Looks professional & non-distracting on large desktop screen  
- Codestral can read & modify `base.html` and `app.py` without confusion

Once Phase 1 is running and looks good — move to Phase 2 (database models & workspace CRUD).

Let me know if you want:
- Ready-to-paste full `app.py` + templates as one block  
- A tiny `matte-bg.jpg` generation prompt  
- Adjustments for specific Bootstrap version / CDN integrity hashes  
- Or jump straight to Phase 2 skeleton prompt for Codestral
```