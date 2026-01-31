# AI Workspace App - Configuration Guide

## Overview

This guide explains how to configure the AI Workspace App, including model parameters, API endpoints, and authentication.

## Configuration Files

### 1. Environment Variables (`.env`)

Create a `.env` file in the `ai-workspace-app/` directory:

```bash
# Flask Secret Key (change in production)
SECRET_KEY=your-secret-key-here

# Grok-Api Configuration
GROK_API_URL=http://localhost:6969
GROK_API_KEY=your-grok-api-key-here
```

**Where to get these values:**
- `SECRET_KEY`: Generate a random string for session encryption
- `GROK_API_URL`: The URL where your Grok-Api server is running
- `GROK_API_KEY`: Your API key for the Grok-Api server (from `Grok-Api/api_users.db`)

### 2. Model Configuration (`config.py`)

The `IMAGE_GENERATION_MODELS` dictionary in [`config.py`](config.py) defines all model parameters:

```python
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
```

**How to add a new model:**

1. Add a new entry to `IMAGE_GENERATION_MODELS` in [`config.py`](config.py):
```python
IMAGE_GENERATION_MODELS = {
    'sdxl': { ... },
    'flux': { ... },
    'your_new_model': {
        'name': 'Your Model Name',
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
```

2. Add the model option to the dropdown in [`templates/workspaces/view.html`](templates/workspaces/view.html):
```html
<select class="form-select bg-dark text-light border-secondary" id="model" name="model" required>
    <option value="sdxl">SDXL (Stable Diffusion XL)</option>
    <option value="flux">Flux Klein</option>
    <option value="your_new_model">Your Model Name</option>
</select>
```

3. Add the generation endpoint in [`Grok-Api/api_server.py`](Grok-Api/api_server.py):
```python
@app.post("/v1/generate/your_new_model")
async def generate_your_new_model(request: ImageGenerationRequest, api_key: str = Depends(get_api_key)):
    # Your implementation here
    pass
```

4. Add the client method in [`api_client.py`](api_client.py):
```python
def generate_your_new_model(self, prompt: str, negative_prompt: str = None,
                           width: int = 768, height: int = 1024,
                           num_steps: int = 20, guidance_scale: float = 8.0,
                           seed: int = -1) -> Dict[str, Any]:
    """Generate an image using Your New Model"""
    # Your implementation here
    pass
```

### 3. Grok-Api Server Configuration

The Grok-Api server is configured in [`Grok-Api/.env`](Grok-Api/.env):

```bash
# API Server Configuration
HOST=0.0.0.0
PORT=6969

# Pixazo API Key (for image generation)
PIXAZO_API_KEY=your-pixazo-api-key-here

# SOCKS5 Proxy (optional)
USE_SOCKS=false
SOCKS=socks5://proxy.example.com:1080

# Debug mode
DEBUG=false
```

**Where to get PIXAZO_API_KEY:**
- This is the API key for the Pixazo image generation service
- Contact Pixazo support or check your Pixazo account dashboard

## API Endpoints

### Grok-Api Server (Port 6969)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/models` | GET | Get available chat models |
| `/v1/chat/completions` | POST | Send chat completion request (supports streaming) |
| `/v1/generate/sdxl` | POST | Generate image with SDXL |
| `/v1/generate/flux` | POST | Generate image with Flux Klein |

### Web App API (Port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models` | GET | Get available image generation models |
| `/api/workspaces/<id>/generate` | POST | Generate image for workspace |
| `/api/workspaces/<id>/images` | GET | Get generated images for workspace |
| `/api/workspaces/<id>/themes` | GET | Get available themes |
| `/api/workspaces/<id>/styles` | GET | Get styles for workspace |

## Image Generation Parameters

### Prompt Building

The final prompt is built as:
```
Theme (before) + Main Prompt + Style (after)
```

Example:
- Theme: "photorealistic, 8k, highly detailed"
- Main Prompt: "a beautiful sunset over mountains"
- Style: "cinematic lighting, dramatic atmosphere"
- Final: "photorealistic, 8k, highly detailed, a beautiful sunset over mountains, cinematic lighting, dramatic atmosphere"

### Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `width` | Image width in pixels | 768 | 256-1536 |
| `height` | Image height in pixels | 1024 | 256-2048 |
| `num_steps` | Number of inference steps | 20 | 10-50 |
| `guidance_scale` | How closely to follow the prompt | 8.0 | 1.0-20.0 |
| `seed` | Random seed for reproducibility | -1 (random) | Any integer |

### Style Parameters

When a style is selected, its parameters are used unless overridden:
- `positive_prompt` - Added after main prompt
- `negative_prompt` - What to avoid in the image
- `cfg_scale` - Guidance scale
- `steps` - Number of inference steps
- `seed` - Random seed
- `model` - Which model to use

## Database Configuration

The web app uses SQLite database stored at:
```
ai-workspace-app/db/workspace.db
```

No additional configuration is needed for development.

## Troubleshooting

### "UndefinedError: 'Theme' is undefined"
**Solution:** Restart the Flask app after making changes to [`app.py`](app.py).

### "Invalid or missing API key"
**Solution:** Check that `GROK_API_KEY` is set in `.env` and matches a key in `Grok-Api/api_users.db`.

### "PIXAZO_API_KEY not configured"
**Solution:** Set `PIXAZO_API_KEY` in `Grok-Api/.env`.

### Image generation timeout
**Solution:** Increase the timeout in [`api_client.py`](api_client.py) or check your network connection.

## Security Notes

1. **Never commit `.env` files** to version control
2. **Use strong secret keys** in production
3. **Enable HTTPS** in production
4. **Set `SESSION_COOKIE_SECURE = True`** in production
5. **Rotate API keys** regularly
