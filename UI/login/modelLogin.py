# -*- coding: utf-8 -*-
"""
Model: business/data logic layer
- Provides a simple credential check
- In real apps, replace with DB/API + hashed passwords
"""
class AuthModel:

    # Fake store. Replace with secure storage/DB.
    _VALID = {
        "admin": "secret123",
        "user": "password"
    }

    def verify(self, username: str, password: str) -> bool:
        """Return True if credentials are valid; otherwise False."""
        stored = self._VALID.get(username)
        return stored is not None and stored == password