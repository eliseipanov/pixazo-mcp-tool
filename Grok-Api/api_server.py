from fastapi      import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
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
import asyncio

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

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify responses are being sent correctly"""
    test_response = {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "grok-3-auto",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a test response"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    }
    logging.info(f"Test endpoint called, returning response")
    return Response(content=json.dumps(test_response, ensure_ascii=False), media_type="application/json")

@app.get("/socks")
@app.post("/socks")
async def socks_check():
    """SOCKS5 proxy check endpoint - checks IP address without API key"""
    try:
        # Check if SOCKS5 proxy is enabled
        use_socks = os.getenv('USE_SOCKS', 'false').lower() == 'true'
        socks_proxy = os.getenv('SOCKS', None)  # Changed from SOCKS5 to SOCKS
        
        # Debug: Log all environment variables
        logging.info(f"SOCKS5 check requested - USE_SOCKS: {use_socks}, SOCKS: {socks_proxy}")
        logging.info(f"Current working directory: {os.getcwd()}")
        logging.info(f"All environment variables: {dict(os.environ)}")
        
        # Try to load .env file explicitly
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        logging.info(f"Loading .env from: {env_path}")
        load_dotenv(env_path)
        
        # Re-read environment variables after loading .env
        use_socks = os.getenv('USE_SOCKS', 'false').lower() == 'true'
        socks_proxy = os.getenv('SOCKS', None)  # Changed from SOCKS5 to SOCKS
        logging.info(f"After loading .env - USE_SOCKS: {use_socks}, SOCKS: {socks_proxy}")
        
        # Use requests with pysocks for SOCKS5 proxy support
        import requests as http_requests
        
        # Configure proxy if SOCKS5 is enabled
        proxies = None
        if use_socks and socks_proxy:
            proxy = format_proxy(socks_proxy)
            proxies = {
                "http": proxy,
                "https": proxy
            }
            logging.info(f"Using SOCKS5 proxy for IP check: {proxy}")
        else:
            logging.warning(f"SOCKS5 proxy not configured - use_socks: {use_socks}, socks_proxy: {socks_proxy}")
        
        # Make request to jsonip.com
        response = http_requests.get('https://jsonip.com/', proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            ip_data = response.json()
            logging.info(f"IP check result: {ip_data}")
            
            result = {
                "status": "success",
                "use_socks": use_socks,
                "socks_proxy": format_proxy(socks_proxy) if use_socks and socks_proxy else None,
                "ip_address": ip_data.get('ip', 'unknown'),
                "location": ip_data.get('city', 'unknown') + ', ' + ip_data.get('country', 'unknown'),
                "isp": ip_data.get('org', 'unknown'),
                "timestamp": ip_data.get('time', 'unknown')
            }
        else:
            logging.error(f"IP check failed with status code: {response.status_code}")
            result = {
                "status": "error",
                "use_socks": use_socks,
                "socks_proxy": format_proxy(socks_proxy) if use_socks and socks_proxy else None,
                "error": f"Failed to check IP address: HTTP {response.status_code}"
            }
        
        return Response(content=json.dumps(result, ensure_ascii=False), media_type="application/json")
    
    except Exception as e:
        logging.error(f"Error in SOCKS5 check: {str(e)}")
        # Get proxy configuration for error response
        use_socks = os.getenv('USE_SOCKS', 'false').lower() == 'true'
        socks_proxy = os.getenv('SOCKS', None)  # Changed from SOCKS5 to SOCKS
        
        result = {
            "status": "error",
            "use_socks": use_socks,
            "socks_proxy": format_proxy(socks_proxy) if use_socks and socks_proxy else None,
            "error": str(e)
        }
        return Response(content=json.dumps(result, ensure_ascii=False), media_type="application/json", status_code=500)

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
        # Check if SOCKS5 proxy should be used
        use_socks = os.getenv('USE_SOCKS', 'false').lower() == 'true'
        
        if use_socks:
            proxy_env = os.getenv('SOCKS', None)  # Changed from SOCKS5 to SOCKS
            if proxy_env:
                proxy = format_proxy(proxy_env)
                logging.info(f"Using SOCKS5 proxy: {proxy}")
            else:
                logging.warning("USE_SOCKS is true but SOCKS environment variable is not set")
                proxy = None
        else:
            proxy = None
            logging.info("SOCKS5 proxy disabled")

        logging.info(f"Processing chat completion with model: {request.model}")
        grok_response = Grok(request.model, proxy).start_convo(full_message)

        # Log the raw response for debugging
        logging.debug(f"Grok response: {grok_response}")
        logging.info(f"Grok response keys: {grok_response.keys() if isinstance(grok_response, dict) else 'Not a dict'}")
        if isinstance(grok_response, dict):
            if "response" in grok_response:
                logging.info(f"Response content: {grok_response['response']}")
            if "error" in grok_response:
                logging.info(f"Error content: {grok_response['error']}")

        # Check if Grok returned an error
        if "error" in grok_response:
            logging.error(f"Grok API error: {grok_response['error']}")
            # Handle both string and dict error formats
            error_data = grok_response['error']
            if isinstance(error_data, str):
                # Try to parse JSON string error
                try:
                    error_dict = json.loads(error_data)
                    error_message = error_dict.get('error', {}).get('message', 'Unknown error')
                except (json.JSONDecodeError, KeyError):
                    error_message = str(error_data)
            elif isinstance(error_data, dict):
                error_message = error_data.get('error', {}).get('message', error_data.get('message', 'Unknown error'))
            else:
                error_message = str(error_data)

            # Return error as valid chat completion response with proper status code
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

            # Return with 502 Bad Gateway status code for Grok API errors
            return Response(
                content=json.dumps(response_data), 
                media_type="application/json",
                status_code=502  # Bad Gateway - Grok API is unavailable
            )

        # Check if we have a valid response
        response_content = grok_response.get("response", "")
        stream_response_tokens = grok_response.get("stream_response", [])
        logging.info(f"Extracted response_content: {response_content[:100] if response_content else 'None'}")
        logging.info(f"Stream response tokens: {len(stream_response_tokens)}")
        
        if not response_content:
            logging.error("No response content from Grok")
            raise HTTPException(status_code=503, detail="No response from Grok API")

        # Check if streaming is requested
        if request.stream:
            logging.info(f"Streaming response requested")
            return StreamingResponse(
                stream_response(stream_response_tokens, request.model),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )

        # Format response in OpenAI style (non-streaming)
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

        logging.info(f"About to send response to client")
        
        # Log the response data being sent to client
        logging.info(f"Sending response to client: {json.dumps(response_data, ensure_ascii=False)}")
        
        # Ensure proper Unicode encoding in JSON response
        json_response = json.dumps(response_data, ensure_ascii=False)
        logging.info(f"JSON response length: {len(json_response)}")
        
        logging.info(f"Returning Response object")
        return Response(content=json_response, media_type="application/json")

    except Exception as e:
        logging.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def stream_response(tokens: list, model: str):
    """Stream response in OpenAI-compatible SSE format using actual tokens from Grok"""
    response_id = f"chatcmpl-{secrets.token_hex(16)}"
    created = int(time.time())
    
    # Stream each token as it arrives from Grok
    for token in tokens:
        chunk_data = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {
                    "content": token
                },
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.01)  # Small delay to simulate streaming
    
    # Send final chunk with finish_reason
    final_chunk = {
        "id": response_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"

if __name__ == "__main__":
    run("api_server:app", host="0.0.0.0", port=6969, workers=5)