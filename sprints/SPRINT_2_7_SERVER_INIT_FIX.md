## Pixazo MCP Tool - Sprint 2.7: Server Initialization Fix

**Objective:** Correct the instantiation of `InitializationOptions` within the `main()` function to satisfy Pydantic schema requirements, based on the reference implementation structure.

### Task SPR2-08: Correct InitializationOptions Instantiation

**Objective:** Provide all required fields for `InitializationOptions` during server setup.

**Instructions:**
1.  In **`mcp_pixazo.py`**, locate the `main()` async function where `init_options` is created.
2.  Replace the failing line:
    ```python
    # OLD (Failing):
    init_options = InitializationOptions()
    ```
3.  **Replace it** with the required structure, ensuring it mirrors the pattern observed in the reference `vanya_mcp.py` for server initialization:
    ```python
    from mcp.server.lowlevel.server import NotificationOptions
    
    # ... inside main() ...
    init_options = InitializationOptions(
        server_name="pixazo-mcp-tool", # Use a specific name for our tool
        server_version="1.0.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
    )
    ```
4.  Ensure that the necessary imports (`NotificationOptions`, `server.get_capabilities`) are present or added if missing.

**Benefits:**
- Resolves the `ValidationError` from Pydantic.
- Ensures the server registers correctly with the MCP host, providing necessary metadata about itself.
