import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PIXAZO_API_KEY = os.getenv("PIXAZO_API_KEY")
    LOG_FILE = os.getenv("LOG_FILE", "logs/mcp_errors.log")
    PIXAZO_CURRENT_MODEL_URL = os.getenv("PIXAZO_CURRENT_MODEL_URL", "https://gateway.pixazo.ai/getImage/v1/getSDXLImage")
    DATABASE_PATH = "data/metadata.db"
    GENERATED_IMAGES_DIR = "data/generated"
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    
    # Generation defaults from environment variables
    DEFAULT_WIDTH = int(os.getenv("PIXAZO_DEFAULT_WIDTH", "768"))
    DEFAULT_HEIGHT = int(os.getenv("PIXAZO_DEFAULT_HEIGHT", "1024"))
    DEFAULT_NUM_STEPS = int(os.getenv("PIXAZO_DEFAULT_NUM_STEPS", "20"))
    DEFAULT_GUIDANCE_SCALE = int(os.getenv("PIXAZO_DEFAULT_GUIDANCE", "8"))  # Minimum of 7
    DEFAULT_SEED = int(os.getenv("PIXAZO_DEFAULT_SEED", "-1"))
