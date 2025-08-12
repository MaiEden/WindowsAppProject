"""
Gateway for external services access. Sends HTTP GET & POST.
"""
import requests

class Gateway:
    def __init__(self, timeout=10):
        self.timeout = timeout

    def get(self, url, params=None, headers=None):
        """get URL query and return response text"""
        try:
            response = requests.get(url, params=params, headers=headers,
                                    timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[Gateway] error GET: {e}")
            return None

    def post(self, url, data=None, json=None, headers=None):
        """Post data to URL and return response text"""
        try:
            response = requests.post(url, data=data, json=json, headers=headers,
                                     timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[Gateway] error POST: {e}")
            return None