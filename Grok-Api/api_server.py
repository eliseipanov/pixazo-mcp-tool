from fastapi      import FastAPI, HTTPException, Response
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
import time
import secrets
import json

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

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    logging.debug(f"Received API key: {api_key}")
    if api_key and api_key.startswith("Bearer "):
        api_key = api_key[7:]
    if not api_key or not validate_api_key(api_key):
        logging.error(f"Invalid or missing API key: {api_key}")
        logging.error(f"Invalid or missing API key: {api_key}")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key

class ConversationRequest(BaseModel):
    proxy: str = None
    proxy: str = None
    message: str
    model: str = "grok-3-auto"
    extra_data: dict = None

def format_proxy(proxy: str) -> str:
    """
    Format proxy string. Supports both HTTP and SOCKS5 proxies.
    For SOCKS5 proxies, returns as-is since curl_cffi handles them.
    """
    if proxy.startswith("socks5://"):
        # SOCKS5 proxy - return as-is for curl_cffi
        return proxy
    elif proxy.startswith(("http://", "https://")):
        # HTTP proxy - return as-is
        return proxy
    else:
        # Assume SOCKS5 if no scheme
        return f"socks5://{proxy}"

@app.get("/v1/models")
async def get_models(api_key: str = Depends(get_api_key)):
    logging.info(f"GET /v1/models called with API key: {api_key}")
    return Models.get_models()

class ChatCompletionRequest(BaseModel):
    model: str = "grok-3-auto"
    messages: list
    max_tokens: int = None
    temperature: float = None
    stream: bool = False

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, api_key: str = Depends(get_api_key)):
    logging.info(f"POST /v1/chat/completions called with API key: {api_key}, model: {request.model}")

    # Extract the last user message
    user_message = None
    system_message = None

    for msg in request.messages:
        if msg["role"] == "user":
            user_message = msg["content"]
        elif msg["role"] == "system":
            system_message = msg["content"]

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    # Build context from conversation history
    context = ""
    if system_message:
        context += f"System: {system_message}\n"

    # Add conversation history (excluding the current user message)
    for msg in request.messages[:-1]:
        if msg["role"] == "user":
            context += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            context += f"Assistant: {msg['content']}\n"

    # Combine context with current message
    full_message = context + f"User: {user_message}"

    try:
        # TEMPORARILY DISABLE PROXY FOR TESTING
        proxy = None
        # proxy_env = os.getenv('SOCKS5', None)
        # if proxy_env:
        #     proxy = format_proxy(proxy_env)
        # else:
        #     proxy = None

        logging.info(f"Processing chat completion with model: {request.model}")
        grok_response = Grok(request.model, proxy).start_convo(full_message)

        # Log the raw response for debugging
        logging.debug(f"Grok response: {grok_response}")

        # Check if Grok returned an error
        if "error" in grok_response:
            logging.error(f"Grok API error: {grok_response['error']}")
            # Handle both string and dict error formats
            error_data = grok_response['error']
            if isinstance(error_data, str):
                # Try to parse JSON string error
                try:
                    import json
                    error_dict = json.loads(error_data)
                    error_message = error_dict.get('error', {}).get('message', 'Unknown error')
                except (json.JSONDecodeError, KeyError):
                    error_message = str(error_data)
            elif isinstance(error_data, dict):
                error_message = error_data.get('error', {}).get('message', error_data.get('message', 'Unknown error'))
            else:
                error_message = str(error_data)

            # Return error as valid chat completion response instead of throwing exception
            response_id = f"chatcmpl-{secrets.token_hex(16)}"
            created = int(time.time())

            response_data = {
                "id": response_id,
                "object": "chat.completion",
                "created": created,
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Grok API Error: {error_message}"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }

            return Response(content=json.dumps(response_data), media_type="application/json")

        # Check if we have a valid response
        response_content = grok_response.get("response", "")
        if not response_content:
            logging.error("No response content from Grok")
            raise HTTPException(status_code=503, detail="No response from Grok API")

        # Format response in OpenAI style
        response_id = f"chatcmpl-{secrets.token_hex(16)}"
        created = int(time.time())

        # Estimate token usage
        prompt_tokens = len(full_message.split()) * 1.3  # Rough estimate
        completion_tokens = len(response_content.split()) * 1.3
        total_tokens = prompt_tokens + completion_tokens

        response_data = {
            "id": response_id,
            "object": "chat.completion",
            "created": created,
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": int(prompt_tokens),
                "completion_tokens": int(completion_tokens),
                "total_tokens": int(total_tokens)
            }
        }

        return Response(content=json.dumps(response_data), media_type="application/json")

    except Exception as e:
        logging.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    run("api_server:app", host="0.0.0.0", port=6969, workers=50)