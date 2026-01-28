## Pixazo MCP Tool - Sprint 1: Core Tool Registration and Hallo Check

**Objective:** Establish the basic structure matching the required MCP server conventions, load configuration, and implement the connectivity check tool.

### Prerequisites
Assume necessary imports (`asyncio`, `requests`, `os`, `types` from `mcp.server.models` and `mcp.types`, and the `server` object initialization) are already present, similar to `vanya_mcp.py`. Assume environment variable `PIXAZO_API_KEY` must be loaded.

---

### Task SPR1-01: Setup Environment & Basic Structure

**Objective:** Load the API Key securely.

**Instructions:**
1.  Implement logic to retrieve `PIXAZO_API_KEY` from environment variables.
2.  If the key is missing, log an error but allow the server initialization to proceed (the actual API call will fail later, but the tool registration must complete).
3.  Create a dummy `config.py` or ensure a placeholder for `config.PROJECT_ROOT` exists for logging purposes if logging is included.

### Task SPR1-02: Implement `hallo_pixazo` Tool

**Objective:** Create the tool that verifies the communication pipe is open.

**Instructions:**
1.  Register a tool named **`hallo_pixazo`** in the `@server.list_tools()` method.
    *   `description`: "Checks connectivity and tool readiness."
    *   `inputSchema`: Empty object `{ "type": "object", "properties": {} }`.
2.  Implement the corresponding handler in `@server.call_tool()`:
    *   If `name == "hallo_pixazo"`, return the required response format: `[types.TextContent(type="text", text="Pixazo Tool Ready.")]`

### Task SPR1-03: Define `pix_generate` Schema

**Objective:** Define the necessary inputs for image generation according to the Pixazo API requirements.

**Instructions:**
1.  Register a tool named **`pix_generate`** in `@server.list_tools()`.
2.  The input schema must minimally require the core parameters needed for the API:
    ```json
    {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "The main text prompt for image generation."},
            "negative_prompt": {"type": "string", "description": "Prompt defining elements to avoid."},
            "width": {"type": "integer", "description": "Output image width (e.g., 1024)."},
            "height": {"type": "integer", "description": "Output image height (e.g., 1024)."}
        },
        "required": ["prompt"] 
    }
    ```
3.  **Note:** We will handle defaults and other parameters in Sprint 2. For now, only the required fields are mandatory for registration.

### Task SPR1-04: Implement `pix_generate` Skeleton

**Objective:** Handle the call for generation, validate essential input, and return a status placeholder.

**Instructions:**
1.  Implement the handler for `name == "pix_generate"` in `@server.call_tool()`.
2.  Check if the mandatory `prompt` argument is present in `arguments`.
3.  If `prompt` is missing, return an error response via `types.TextContent`.
4.  If validation passes, return a success placeholder indicating that the API call preparation will follow: `[types.TextContent(type="text", text="Generation request received. API initiation in next sprint.")]`

---
