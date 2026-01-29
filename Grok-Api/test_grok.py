import requests

response = requests.post(
    "http://localhost:6969/ask",
    json={
        "proxy": "https://127.0.0.1:16379",
        "message": "Hello, Grok!",
        "model": "grok-3-fast",
        "extra_data": None
    }
)
print(response.json())