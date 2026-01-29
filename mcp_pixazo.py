import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from config import Config
import os
import sys
import requests
import json
from datetime import datetime
from db_manager import initialize_db, save_metadata
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()

# Determine project root path from command line arguments
def get_project_root():
    """Determine the project root path from --project-dir argument or fallback to script directory."""
    # Default fallback: directory where the script resides
    root_path = os.path.abspath(os.path.dirname(__file__))
    
    # Check for --project-dir argument
    if "--project-dir" in sys.argv:
        try:
            dir_index = sys.argv.index("--project-dir") + 1
            if dir_index < len(sys.argv):
                provided_path = sys.argv[dir_index]
                # Ensure the path is absolute
                if os.path.isabs(provided_path):
                    root_path = provided_path
                else:
                    root_path = os.path.abspath(provided_path)
                print(f"Using project root from --project-dir: {root_path}")
            else:
                print("Warning: Found --project-dir flag but no path specified. Using script directory.")
        except IndexError:
            print("Warning: Found --project-dir flag but no path specified. Using script directory.")
    
    return root_path

# Set global project root
GLOBAL_PROJECT_ROOT = get_project_root()
print(f"Project root determined as: {GLOBAL_PROJECT_ROOT}")

# Update config paths to use the global project root
Config.DATABASE_PATH = os.path.join(GLOBAL_PROJECT_ROOT, "data", "metadata.db")
Config.GENERATED_IMAGES_DIR = os.path.join(GLOBAL_PROJECT_ROOT, "data", "generated")
Config.LOG_FILE = os.path.join(GLOBAL_PROJECT_ROOT, "logs", "mcp_errors.log")

# Define absolute image storage path
GENERATED_IMAGES_DIR = os.path.join(GLOBAL_PROJECT_ROOT, "data", "generated", "default")

# Ensure the directory structure exists
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)

server = Server("MCP_PIXAZO")

# Load API Key and validate environment
PIXAZO_API_KEY = os.getenv("PIXAZO_API_KEY")
if not PIXAZO_API_KEY:
    print("Warning: PIXAZO_API_KEY environment variable not set. Tool registration will proceed but API calls will fail.")

# Initialize database on startup
try:
    initialize_db(Config.DATABASE_PATH)
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")

def download_image(image_url: str, save_path: str) -> bool:
    """
    Download image from remote URL and save locally.
    
    Args:
        image_url (str): URL of the image to download
        save_path (str): Local path to save the image
    
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False

def get_generation_defaults() -> dict:
    """
    Load generation defaults from environment variables.
    
    Returns:
        dict: Dictionary of default generation parameters
    """
    return {
        "height": Config.DEFAULT_HEIGHT,
        "width": Config.DEFAULT_WIDTH,
        "num_steps": Config.DEFAULT_NUM_STEPS,
        "guidance_scale": Config.DEFAULT_GUIDANCE_SCALE,  # Minimum of 7
        "seed": Config.DEFAULT_SEED
    }

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="hallo_pixazo",
            description="Checks connectivity and tool readiness.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="pix_generate",
            description="Generate images using Pixazo API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The main text prompt for image generation."},
                    "negative_prompt": {"type": "string", "description": "Prompt defining elements to avoid."},
                    "width": {"type": "integer", "description": "Output image width (e.g., 1024)."},
                    "height": {"type": "integer", "description": "Output image height (e.g., 1024)."},
                    "num_steps": {"type": "integer", "description": "Number of generation steps (e.g., 20)."},
                    "guidance_scale": {"type": "integer", "description": "Guidance scale for generation (e.g., 5)."},
                    "seed": {"type": "integer", "description": "Random seed for reproducible generation (e.g., 42)."}
                },
                "required": ["prompt"]
            },
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "hallo_pixazo":
        return [types.TextContent(type="text", text="Pixazo Tool Ready.")]
    elif name == "pix_generate":
        # Validate required prompt parameter
        if "prompt" not in arguments:
            return [types.TextContent(type="text", text="Error: 'prompt' is required for pix_generate tool.")]
        
        # Construct timestamp for metadata
        timestamp = datetime.now().isoformat()
        
        try:
            # Load defaults from environment variables
            defaults = get_generation_defaults()
            
            # Merge caller arguments with defaults (caller arguments take precedence)
            data_payload = defaults.copy()
            data_payload.update(arguments)
            
            # Define endpoint and headers
            PIXAZO_URL = "https://gateway.pixazo.ai/getImage/v1/getSDXLImage"
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache',
                'Ocp-Apim-Subscription-Key': PIXAZO_API_KEY,
            }
            
            # Make the API request
            response = requests.post(PIXAZO_URL, headers=headers, json=data_payload)
            
            # Success handling (HTTP 200)
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    image_url = response_data.get('imageUrl')
                    
                    # Generate unique filename for local storage
                    filename = f"pixazo_{uuid.uuid4().hex[:16]}.png"
                    local_save_path = os.path.join(GENERATED_IMAGES_DIR, filename)
                    
                    # Download the image
                    download_success = download_image(image_url, local_save_path)
                    
                    if download_success:
                        # Save metadata to database with local path
                        metadata = {
                            'timestamp': timestamp,
                            'prompt': arguments['prompt'],
                            'parameters_json': arguments,  # Store original arguments only
                            'image_url': local_save_path,  # Store local path
                            'status': 'SUCCESS'
                        }
                        save_metadata(Config.DATABASE_PATH, metadata)
                        
                        return [types.TextContent(type="text", text=f"Image generated and saved successfully! Local path: {local_save_path}")]
                    else:
                        # Download failed, save error metadata
                        metadata = {
                            'timestamp': timestamp,
                            'prompt': arguments['prompt'],
                            'parameters_json': arguments,  # Store original arguments only
                            'image_url': image_url,  # Store remote URL for reference
                            'status': 'DOWNLOAD_FAILED'
                        }
                        save_metadata(Config.DATABASE_PATH, metadata)
                        
                        return [types.TextContent(type="text", text=f"Image generated but download failed. Remote URL: {image_url}")]
                    
                except json.JSONDecodeError:
                    error_msg = "Error: Invalid JSON response from Pixazo API"
                    metadata = {
                        'timestamp': timestamp,
                        'prompt': arguments['prompt'],
                        'parameters_json': arguments,  # Store original arguments only
                        'image_url': None,
                        'status': f'HTTP_{response.status_code}'
                    }
                    save_metadata(Config.DATABASE_PATH, metadata)
                    return [types.TextContent(type="text", text=error_msg)]
            
            # Error handling (HTTP 4xx/5xx)
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f'HTTP {response.status_code}: {response.reason}')
                except json.JSONDecodeError:
                    error_msg = f'HTTP {response.status_code}: {response.reason}'
                
                # Save error metadata to database
                metadata = {
                    'timestamp': timestamp,
                    'prompt': arguments['prompt'],
                    'parameters_json': arguments,  # Store original arguments only
                    'image_url': None,
                    'status': f'HTTP_{response.status_code}'
                }
                save_metadata(Config.DATABASE_PATH, metadata)
                
                return [types.TextContent(type="text", text=f"Error generating image: {error_msg}")]
                
        except Exception as e:
            # Handle any other exceptions
            metadata = {
                'timestamp': timestamp,
                'prompt': arguments['prompt'],
                'parameters_json': arguments,  # Store original arguments only
                'image_url': None,
                'status': 'EXCEPTION'
            }
            save_metadata(Config.DATABASE_PATH, metadata)
            return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

import asyncio
import signal
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel.server import NotificationOptions

async def monitor_stdin(read_stream):
    """Monitor stdin for shutdown signal."""
    try:
        while True:
            line = await read_stream.readline()
            if not line:
                break
    except asyncio.CancelledError:
        pass

async def main():
    """Main server execution function."""
    # Set up signal handlers
    def signal_handler(signum, frame):
        print(f"Received signal {signum}, shutting down...")
        raise KeyboardInterrupt()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            # Initialize with proper options for Pydantic validation
            init_options = InitializationOptions(
                server_name="pixazo-mcp-tool",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
            
            # Start monitoring stdin
            monitor_task = asyncio.create_task(monitor_stdin(read_stream))
            
            try:
                # Run the server with the correct MCP framework pattern
                await server.run(
                    read_stream,
                    write_stream,
                    init_options
                )
            finally:
                # Clean up monitor task
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass
    except KeyboardInterrupt:
        print("Server shutdown requested by user")
    except Exception as e:
        print(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
