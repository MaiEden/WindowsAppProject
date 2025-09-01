"""
Model for Sign Up
"""

from typing import Tuple
from UI import server_access


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
        user = server_access.request(f"/DB/users/get_user_by_name/{username}")
        if user:
            return False, "Username already exists."

        # Rule: password length
        if len(ph) < 6:
            return False, "Password must be at least 6 characters."

        # Insert the new user into the database
        server_access.request(f"/DB/users/insert_user/{phone}/{username}/{password_hash}/{region}")
        print(server_access.request(f"/DB/users/get_user_by_name/{username}"))  # Debug: print the newly created user
        return True, "Account created successfully."