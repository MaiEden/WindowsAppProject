"""
Model for Sign Up
"""

from typing import Dict, Tuple, Any

class SignUpModel:

    def register(self, phone: str, username: str, password_hash: str, region: str) -> Tuple[bool, str]:
        """
        Attempt to create an account. Returns (ok, message).
        """
        u = username or ""
        p = (phone or "").strip()
        ph = password_hash or ""
        r = region or ""

        # Required fields
        if not (p and u and ph and r):
            return False, "All fields are required."

        # Uniqueness
        if u in self._users:
            return False, "Username already exists."

        # Simple rule: password length
        if len(ph) < 6:
            return False, "Password must be at least 6 characters."

        # In real apps: hash password securely and persist to DB
        self._users[u] = {"phone": p, "passwordHash": ph, "region": r}
        return True, "Account created successfully."
