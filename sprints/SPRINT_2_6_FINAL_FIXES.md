## Pixazo MCP Tool - Sprint 2.6: Final Critical Fixes

**Objective:** Resolve the API Key loading failure and correct the server startup procedure to match the expected MCP framework convention.

### Task SPR2-06 (API KEY FIX): Ensure Environment Loading

**Objective:** Correctly load environment variables from the `.env` file.

**Instructions:**
1.  In **`mcp_pixazo.py`**, add the necessary import: `from dotenv import load_dotenv`.
2.  At the absolute beginning of the script (before logging setup), call `load_dotenv()`.
3.  Ensure the warning message related to missing `PIXAZO_API_KEY` is suppressed if the key is present in the loaded environment.

### Task SPR2-07 (SERVER STARTUP FIX): Correct Server Execution

**Objective:** Replace the failing server execution block in `main()` with the functional block seen in the reference `vanya_mcp.py`.

**Instructions:**
1.  Locate the `try...finally` block within the `main()` async function in **`mcp_pixazo.py`**.
2.  Replace the failing server execution logic with the following structure (which correctly uses the context manager streams):
    ```python
    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(...) # Use existing initialization code

        monitor_task = asyncio.create_task(monitor_stdin(read_stream))

        try:
            # THIS IS THE CORRECT CALL PATTERN BASED ON REFERENCE CODE
            await server.run(
                read_stream,
                write_stream,
                init_options
            )
        finally:
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
    ```
    *(Note: Ensure that `monitor_stdin` is defined and correctly handles streams, as shown in the reference code.)*

---
