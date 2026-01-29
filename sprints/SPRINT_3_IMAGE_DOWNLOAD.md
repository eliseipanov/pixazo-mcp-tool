## Pixazo MCP Tool - Sprint 3: Image Download and Local Storage (Configuration Driven)

**Objective:** Implement image workflow, loading all default generation settings from environment variables instead of hardcoding them.

### Prerequisites
- `GLOBAL_PROJECT_ROOT` is set.
- `PIXAZO_API_KEY` is accessible.
- **Crucially:** Environment variables must be defined for all generation defaults (e.g., `PIXAZO_DEFAULT_WIDTH`, `PIXAZO_DEFAULT_GUIDANCE`).

---

### Task SPR3-01: Define Absolute Image Storage Path & Setup Directories

**Objective:** Establish and ensure the target directory for saved images exists.

**Instructions:**
1.  Define the absolute directory path using `GLOBAL_PROJECT_ROOT`:
    `GENERATED_IMAGES_DIR = os.path.join(GLOBAL_PROJECT_ROOT, "data", "generated", "default")`
2.  Ensure this directory structure is created before any file writing.

### Task SPR3-02: Implement `download_image` Utility Function

**Objective:** Create a utility to fetch binary image data from the remote URL.

**Instructions:**
1.  Implement `download_image(image_url: str, save_path: str) -> bool` in `mcp_pixazo.py`.
2.  Use `requests.get(image_url, stream=True)` and save content safely in binary mode (`'wb'`). Return `True` on success, `False` on failure.

### Task SPR3-03: Complete `pix_generate` Logic (Parameter Loading & API Call)

**Objective:** Map known JSON inputs, load defaults from environment, call the API securely, and manage download.

**Instructions:**
1.  **Environment Default Loading:**
    *   Define a function or logic to read required generation settings from the environment/config. **If an environment variable is missing, use a sensible default (e.g., Height=1024, Guidance=7, Seed=-1)**.
    *   **Crucial Default Update:** The default for `guidance_scale` must be at least **7**.

2.  **Parameter Extraction & Payload Construction:**
    *   In the handler for `pix_generate`, extract known parameters from input `arguments`.
    *   Construct the `pixazo_payload` dictionary.
    *   If a Pixazo parameter (e.g., `num_steps`) is **missing** from the input `arguments`, fetch its value from the **environment/config defaults** defined in step 1.

3.  **Secure API Call:**
    *   Construct mandatory HTTP headers (as defined in Sprint 2).
    *   Execute the request: `response = requests.post(PIXAZO_URL, headers=headers, json=pixazo_payload)`.

4.  **Handling HTTP Response (200 vs. Error Codes):**
    *   **If `response.status_code == 200` (Success):**
        *   Extract `imageUrl`.
        *   Call `download_image()` to save the file locally (generate unique filename).
        *   If download succeeds, call `db_manager.save_metadata()` with **Status: 'SUCCESS'** and the **local `final_save_path`**.
        *   Return success message with the local path.
    *   **If `response.status_code != 200` (API Error):**
        *   Log the error.
        *   Call `db_manager.save_metadata()` with **Status: 'HTTP\_[StatusCode]'**.
        *   Return error message reflecting the HTTP status.

### Task SPR3-04: Comprehensive Metadata Logging

**Objective:** Ensure ALL input arguments received from Msty (`arguments` dictionary) are preserved in the database.

**Instructions:**
1.  When calling `db_manager.save_metadata()` (success or failure), ensure the **entire original `arguments` dictionary** is serialized as JSON and stored in the `parameters_json` field. This preserves fields like `THEME`, which are important for your internal workflow but ignored by the Pixazo API call.
