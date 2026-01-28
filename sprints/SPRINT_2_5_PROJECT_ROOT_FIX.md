## Pixazo MCP Tool - Sprint 2.5: Fixing Project Root Context

**Objective:** Ensure the tool correctly determines the absolute project root path, accounting for the `--project-dir` argument passed by the MCP server launcher.

### Prerequisites
- The server startup command may pass `--project-dir /path/to/project`.
- We must use this path to set the base for all relative file operations (logs, database).

---

### Task SPR2-05 (FIX): Implement Project Root Detection

**Objective:** Parse command-line arguments to find the `--project-dir` value.

**Instructions:**
1.  In the main execution block (`if __name__ == "__main__":`) of **`mcp_pixazo.py`** (or within `main()` before server startup):
    *   Parse `sys.argv` to search for the argument `--project-dir`.
    *   If found, capture the subsequent value as the `PROJECT_ROOT_PATH`.
    *   If *not* found, fall back to using the directory where the script itself resides (the current implementation's best guess).
2.  Define a global or accessible variable (e.g., `GLOBAL_PROJECT_ROOT`) using this determined path.
3.  **Update File Operations:** Modify the file path logic in **`db_manager.py`** (SPR2-01) and logging in **`mcp_pixazo.py`** (SPR1-01) to construct paths relative to this newly determined `GLOBAL_PROJECT_ROOT` instead of relying purely on relative paths or existing `config.PROJECT_ROOT`.

**Example Fallback Logic (Coders should refine this):**
If `--project-dir` is found, `PROJECT_ROOT` becomes that path. Otherwise, use the directory of the currently executing script.

```python
# Pseudocode for implementation in mcp_pixazo.py main block:
# ... after signal handlers ...
# Find project root from arguments
root_path = os.path.abspath(os.path.dirname(__file__)) # Default fallback
if "--project-dir" in sys.argv:
    try:
        dir_index = sys.argv.index("--project-dir") + 1
        if dir_index < len(sys.argv):
            root_path = sys.argv[dir_index]
    except IndexError:
        logging.warning("Found --project-dir flag but no path specified. Using script directory.")

# Set this root path globally or pass it to config/initialization
# For now, ensure all relative paths (data/, logs/) are resolved against this absolute root_path.
