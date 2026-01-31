# Model Templates Documentation

## Overview

The AI Workspace app now supports JSON templates for handling different API request/response formats for different image generation models (SDXL, Flux Klein, etc.).

## Database Schema

The `generative_models` table now includes two new columns:

- `request_template` (TEXT): JSON template for building API requests
- `response_template` (TEXT): JSON template for parsing API responses

## Template Format

### Request Template

```json
{
  "endpoint": "/v1/generate/sdxl",
  "include_params": ["prompt", "width", "height", "num_steps", "guidance_scale", "seed"],
  "exclude_params": [],
  "param_mapping": {}
}
```

**Fields:**
- `endpoint`: API endpoint path (relative to base URL)
- `include_params`: List of parameters to include in request (if empty, all are included)
- `exclude_params`: List of parameters to exclude from request
- `param_mapping`: Map of parameter names to API-specific names

### Response Template

```json
{
  "image_url_path": "imageUrl",
  "success_path": "status",
  "error_path": "error"
}
```

**Fields:**
- `image_url_path`: Path to image URL in response (supports dot notation for nested objects)
- `success_path`: Path to success status in response
- `error_path`: Path to error message in response

## Default Templates

### SDXL Model

**Request Template:**
```json
{
  "endpoint": "/v1/generate/sdxl",
  "include_params": ["prompt", "width", "height", "num_steps", "guidance_scale", "seed"],
  "exclude_params": [],
  "param_mapping": {}
}
```

**Response Template:**
```json
{
  "image_url_path": "imageUrl",
  "success_path": "status",
  "error_path": "error"
}
```

### Flux Klein Model

**Request Template:**
```json
{
  "endpoint": "/v1/generate/flux",
  "include_params": ["prompt", "width", "height", "num_steps", "seed"],
  "exclude_params": ["guidance_scale"],
  "param_mapping": {
    "num_steps": "num_inference_steps"
  }
}
```

**Response Template:**
```json
{
  "image_url_path": "output",
  "success_path": "status",
  "error_path": "error"
}
```

## Setup Instructions

### 1. Run Migration

Add the new columns to the database:

```bash
cd /var/www/pixazo/ai-workspace-app
/var/www/pixazo/.venv/bin/python migrate_add_templates.py
```

### 2. Seed Default Templates

Populate the templates for existing models:

```bash
/var/www/pixazo/.venv/bin/python seed_model_templates.py
```

### 3. Restart Flask App

Restart your Flask application to apply the changes.

## Adding New Models

When adding a new model to the database, you can specify custom templates:

```python
from models import GenerativeModel

new_model = GenerativeModel(
    name='new-model',
    display_name='New Model',
    api_url='https://api.example.com/generate',
    request_template='{"endpoint": "/v1/generate", ...}',
    response_template='{"image_url_path": "data.url", ...}',
    # ... other fields
)
db.session.add(new_model)
db.session.commit()
```

## Editing Templates

You can edit templates directly in the database using the admin interface (if available) or via Python scripts:

```python
from app import app, db, GenerativeModel
import json

with app.app_context():
    model = GenerativeModel.query.filter_by(name='flux').first()
    model.request_template = json.dumps({...})
    model.response_template = json.dumps({...})
    db.session.commit()
```

## Backward Compatibility

The system maintains backward compatibility. If a model doesn't have templates defined, it will use the default behavior (hardcoded endpoints and parameter names).

## Troubleshooting

### Template Not Working

1. Check that templates are valid JSON
2. Verify the `image_url_path` matches the actual API response
3. Check logs for template parsing errors

### Wrong Parameters Sent

1. Verify `include_params` and `exclude_params` in request template
2. Check `param_mapping` for correct parameter names
3. Review API logs to see what's being sent

### Image URL Not Found

1. Verify `image_url_path` in response template
2. Check API response structure
3. Use dot notation for nested paths (e.g., "data.image.url")
