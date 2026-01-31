"""
API Client for Grok-Api server
Handles communication with the Grok-Api for chat and image generation
"""

import requests
import logging
from typing import Optional, Dict, Any
from flask import current_app

logger = logging.getLogger(__name__)


class GrokAPIClient:
    """Client for interacting with Grok-Api server"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the Grok-Api server (default: http://localhost:6969)
            api_key: API key for authentication (default: from config)
        """
        self.base_url = base_url or current_app.config.get('GROK_API_URL', 'http://localhost:6969')
        self.api_key = api_key or current_app.config.get('GROK_API_KEY', '')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to the Grok-Api server
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            data: Request payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=120)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=120)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise Exception(f"Request timeout: {url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Request failed: {e}")
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get available models
        
        Returns:
            Dictionary with available models
        """
        return self._make_request('GET', '/v1/models')
    
    def chat_completion(self, messages: list, model: str = "grok-3-auto", 
                       stream: bool = False, max_tokens: int = None,
                       temperature: float = None) -> Dict[str, Any]:
        """
        Send a chat completion request
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (default: grok-3-auto)
            stream: Whether to stream the response (default: False)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Chat completion response
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if temperature:
            payload["temperature"] = temperature
        
        return self._make_request('POST', '/v1/chat/completions', payload)
    
    def generate_image_via_api_server(self, model: str, prompt: str, negative_prompt: str = None,
                                     width: int = 768, height: int = 1024,
                                     num_steps: int = 20, guidance_scale: float = 8.0,
                                     seed: int = -1, pixazo_api_key: str = None) -> Dict[str, Any]:
        """
        Generate an image by calling the Grok-Api server
        
        Args:
            model: Model to use ("sdxl" or "flux")
            prompt: Main prompt for image generation
            negative_prompt: Negative prompt (what to avoid)
            width: Image width (default: 768)
            height: Image height (default: 1024)
            num_steps: Number of inference steps (default: 20)
            guidance_scale: Guidance scale (default: 8.0)
            seed: Random seed (-1 for random)
            pixazo_api_key: Pixazo API key for this model (from database)
            
        Returns:
            Dictionary with image_url and parameters
        """
        # Determine endpoint based on model
        if model == "sdxl":
            endpoint = "/v1/generate/sdxl"
        elif model == "flux":
            endpoint = "/v1/generate/flux"
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_steps": num_steps,
            "guidance_scale": guidance_scale,
            "seed": seed if seed is not None else -1,
            "model": model
        }
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        # Add Pixazo API key if provided
        if pixazo_api_key:
            payload["pixazo_api_key"] = pixazo_api_key
        
        try:
            logger.info(f"Calling Grok-Api server: {self.base_url}{endpoint}")
            logger.info(f"Request payload: {payload}")
            
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=payload,
                timeout=120
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text[:500]}")  # First 500 chars
            
            if response.status_code == 200:
                response_data = response.json()
                image_url = response_data.get('image_url')
                
                logger.info(f"Image generation successful: {image_url}")
                
                return {
                    "status": "success",
                    "image_url": image_url,
                    "model": model,
                    "parameters": payload
                }
            else:
                error_msg = f"API error: HTTP {response.status_code}"
                logger.error(error_msg)
                logger.error(f"Response body: {response.text}")
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "API timeout"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Image generation error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)


def build_generation_prompt(theme_prompt: str, main_prompt: str, style_prompt: str) -> str:
    """
    Build the final prompt for image generation
    
    Combines theme, main prompt, and style in the correct order:
    Theme (before) + Main Prompt + Style (after)
    
    Args:
        theme_prompt: Theme prompt (added before main prompt)
        main_prompt: Main user prompt
        style_prompt: Style prompt (added after main prompt)
        
    Returns:
        Combined prompt string
    """
    parts = []
    
    if theme_prompt:
        parts.append(theme_prompt.strip())
    
    if main_prompt:
        parts.append(main_prompt.strip())
    
    if style_prompt:
        parts.append(style_prompt.strip())
    
    return ", ".join(parts)
