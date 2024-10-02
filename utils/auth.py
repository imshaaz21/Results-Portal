import os
import hashlib


class AdminAuth:
    # In-memory "database"
    _users_db = {}

    def __init__(self):
        self.initialize_db()

    def initialize_db(self):
        """Initializes the in-memory database with an admin user."""
        # Retrieve admin password from environment variable
        admin_password = os.getenv("ADMIN_PASSWORD")

        # Check if the password is provided in the environment variable
        if not admin_password:
            raise ValueError("Admin password not set. Please set the ADMIN_PASSWORD environment variable.")

        # Add the admin credentials (username: admin, password from environment variable)
        if "admin" not in self._users_db:
            self._users_db["admin"] = self.hash_password(admin_password)

    @staticmethod
    def hash_password(password):
        """Hashes a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        """Validates the username and password against the in-memory database."""
        hashed_password = self.hash_password(password)
        # Check if the user exists in the in-memory database and the password matches
        return self._users_db.get(username) == hashed_password
