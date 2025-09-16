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

def post(path: str, json: Optional[Dict[str, Any]] = None) -> Any:
    """
    JSON POST helper to match the pattern of server_access.request().
    It returns JSON if possible, otherwise raw text.
    """
    url = f"{base_url}{path}"
    resp = requests.post(url, json=json or {})
    resp.raise_for_status()
    try:
        return resp.json()
    except Exception:
        # Some simple endpoints may return plain int in text
        return resp.text