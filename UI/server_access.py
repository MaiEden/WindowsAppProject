import requests
from typing import Any, Dict, Optional

base_url = "http://127.0.0.1:8000"
def request(
    path: str,
    method: str = "GET"
) -> Any:
    url = f"{base_url}{path}"
    response = requests.request(method, url)
    response.raise_for_status()
    return response.json()
