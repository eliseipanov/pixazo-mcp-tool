import requests
from core import Log, Grok
from dotenv import load_dotenv
import os
from json import dumps

proxy = os.getenv('SOCKS')

response = requests.post(
    "http://localhost:6969/ask",
    json={
        "proxy": proxy,
        "message": "Hello, Grok!",
        "model": "grok-4",
        "extra_data": None
    }
)
print(response.json())