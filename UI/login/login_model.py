"""
Model: business/data logic layer
- Provides a simple credential check
- In real apps, replace with DB/API + hashed passwords
"""
from UI import server_access

class AuthModel:

    def verify(self, username: str, password: str) -> bool:
        """Return True if credentials are valid; otherwise False."""
        user = server_access.request(f"/DB/users/get_user_by_name/{username}")
        if not user:
            return False
        # Assuming user is a dictionary with 'password' key
        stored_password = user['PasswordHash']
        if not stored_password:
            return False
        # Compare the provided password with the stored password
        return stored_password == password