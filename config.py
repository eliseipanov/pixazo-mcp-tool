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
