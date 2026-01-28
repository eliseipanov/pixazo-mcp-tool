Here’s the refined **project manifest** in Markdown (ready to copy-paste):

```markdown
# Pixazo MCP Tool
**CLI utility for Pixazo.ai image generation via API**

## Goals
- Generate images from prompts/parameters via Pixazo API.
- Store results in `data/generated/[theme]/` with metadata  of generation in SQLite.
- Support future scaling (async/batch requests).

## Tech Stack
- **Language:** Python 3.10+
- **Libraries:**
  - `requests` (API calls)
  - `click` (CLI)
  - `sqlite3` (metadata storage)
  - `Pillow` (image handling, optional)
  - `mcp` (mcp tool for ai models using this project)
  
- **Environment:** WSL, `.venv`, VSCode + Kilo Hub