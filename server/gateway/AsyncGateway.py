"""
Gateway for external services access. Sends HTTP GET & POST. Do async version using httpx.
"""
import httpx

class AsyncGateway:
    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    async def get(self, url: str, params: dict = None, headers: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def post(self, url: str, data: dict = None, json: dict = None, headers: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, data=data, json=json, headers=headers)
            resp.raise_for_status()
            return resp.json()
