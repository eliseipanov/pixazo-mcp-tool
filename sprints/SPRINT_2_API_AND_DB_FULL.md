## Pixazo MCP Tool - Sprint 2: API Integration and Data Persistence (Refined)

**Objective:** Implement full functionality for image generation via Pixazo API and store metadata in SQLite.

### Prerequisites
- `PIXAZO_API_KEY` loaded.
- `requests` library available.
- Defaults for Pixazo parameters are: `height=1024`, `width=1024`, `num_steps=20`, `guidance_scale=5` (as Integer), `seed=42`.

---

### Task SPR2-01: Implement SQLite Initialization (`db_manager.py`)

**Objective:** Set up the database structure.

**Instructions:**
1.  Create **`db_manager.py`**.
2.  Implement `initialize_db(db_path: str)` to connect to the database (path defined by `config.DB_PATH` e.g., `data/pixazo_metadata.db`).
3.  Create the `generations` table with the following schema:
    ```sql
    CREATE TABLE IF NOT EXISTS generations (
        id INTEGER PRIMARY KEY,
        timestamp TEXT NOT NULL,
        prompt TEXT NOT NULL,
        parameters_json TEXT,
        image_url TEXT,
        status TEXT NOT NULL
    );
    ```

### Task SPR2-02: Implement `save_metadata` Function (`db_manager.py`)

**Objective:** Create the persistence layer function.

**Instructions:**
1.  In **`db_manager.py`**, implement `save_metadata(db_path: str, data: dict)`.
2.  This function must accept a dictionary containing: `timestamp`, `prompt`, `parameters_json`, `image_url`, and `status`.
3.  Insert this data into the `generations` table. Use `json.dumps` on the parameters dictionary before insertion.

### Task SPR2-03: Update `pix_generate` Tool Schema (`mcp_pixazo.py`)

**Objective:** Update the MCP Tool registration schema to recognize all known parameters.

**Instructions:**
1.  In the `@server.list_tools()` section of `mcp_pixazo.py`, update the `inputSchema` for `pix_generate` to include all known optional parameters as defined in the provider documentation (Type: Integer/String as appropriate).
    *   *Note: These fields are optional in the JSON Schema but **must** be present in the payload construction logic later.*

### Task SPR2-04: Complete `pix_generate` HTTP Logic

**Objective:** Construct and send the POST request to Pixazo.

**Instructions:**
1.  Inside the `pix_generate` handler in **`mcp_pixazo.py`**:
    *   Retrieve `PIXAZO_API_KEY`.
    *   Define the static endpoint: `PIXAZO_URL = "https://gateway.pixazo.ai/getImage/v1/getSDXLImage"`.
    *   Construct the final request payload (`data_payload`):
        *   Start with caller arguments (`kwargs`).
        *   Merge required defaults (`height=1024`, `guidance_scale=5`, etc.) **only if the caller did not provide them.**
    *   Construct mandatory HTTP headers:
        ```python
        headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': PIXAZO_API_KEY,
        }
        ```
    *   Execute the POST request using `requests.post(PIXAZO_URL, headers=headers, json=data_payload)`.

### Task SPR2-05: Response Parsing, Error Handling, and Metadata Logging

**Objective:** Handle success and failure codes according to provider documentation and persist results.

**Instructions:**
1.  **Success Handling (HTTP 200):**
    *   Check if `response.status_code == 200`.
    *   Parse the JSON response to extract `imageUrl`.
    *   Call `db_manager.save_metadata()` with status `'SUCCESS'`.
    *   Return the success message containing the URL to the MCP client.
2.  **Error Handling (HTTP 4xx/5xx):**
    *   If status code is not 200, extract the error message (try to parse JSON body for `"error"` key first; otherwise, use status text).
    *   Call `db_manager.save_metadata()` with status set to the HTTP code (e.g., `'HTTP_401'`, `'HTTP_500'`).
    *   Return an informative error message to the MCP client, referencing the status code.
