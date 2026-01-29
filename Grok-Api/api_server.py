from fastapi      import FastAPI, HTTPException
from urllib.parse import urlparse, ParseResult
from pydantic     import BaseModel
from core         import Grok
from uvicorn      import run


from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from core.models import Models
from db import validate_api_key

from dotenv import load_dotenv
import os
import logging

load_dotenv()

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/pixazo/logs/Grok-Api.log'),
        logging.StreamHandler()
    ]
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/www/pixazo/logs/Grok-Api.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or not validate_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key

class ConversationRequest(BaseModel):
    proxy: str = None
    message: str
    model: str = "grok-3-auto"
    extra_data: dict = None

def format_proxy(proxy: str) -> str:
    
    if not proxy.startswith(("http://", "https://")):
        proxy: str = "http://" + proxy
    
    try:
        parsed: ParseResult = urlparse(proxy)

        if parsed.scheme not in ("http", ""):
            raise ValueError("Not http scheme")

        if not parsed.hostname or not parsed.port:
            raise ValueError("No url and port")

        if parsed.username and parsed.password:
            return f"http://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}"
        
        else:
            return f"http://{parsed.hostname}:{parsed.port}"
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid proxy format: {str(e)}")

@app.get("/v1/models")
async def get_models(api_key: str = Depends(get_api_key)):
    return Models.get_models()
    if not request.proxy or not request.message:
        raise HTTPException(status_code=400, detail="Proxy and message are required")
    
    proxy = format_proxy(request.proxy)
    
    try:
        answer: dict = Grok(request.model, proxy).start_convo(request.message, request.extra_data)

        return {
            "status": "success",
            **answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    run("api_server:app", host="0.0.0.0", port=6969, workers=50)