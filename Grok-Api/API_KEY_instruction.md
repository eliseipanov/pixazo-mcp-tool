# API Key Management Guide

## Generating API Keys

To generate a new API key for the Grok-Api sub-project, follow these steps:

1. Navigate to the Grok-Api directory:
   ```bash
   cd /var/www/pixazo/Grok-Api
   ```

2. Run the following command to generate a new API key:
   ```bash
   /var/www/pixazo/.venv/bin/python Grok-Api/cli.py generate
   ```

3. To generate an API key with an expiration date, use the `--expiration-days` option:
   ```bash
   /var/www/pixazo/.venv/bin/python cli.py generate --expiration-days 30
   ```

The generated API key will be displayed in the terminal output.

## Using API Keys

To use the generated API key, include it in the `X-API-KEY` header of your requests to the Grok-Api server. For example:

```bash
curl -X POST http://0.0.0.0:6969/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: YOUR_API_KEY" \
  -d '{"message": "Hello, Grok!"}'
```

## Managing API Keys

All generated API keys are stored in the SQLite database located at `api_users.db` in the Grok-Api directory. You can manage API keys using the provided CLI commands.