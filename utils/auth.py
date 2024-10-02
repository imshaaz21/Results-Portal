import os
import hashlib


class AdminAuth:
    # In-memory "database"
    _users_db = {}

    def __init__(self):
        self.initialize_db()  # Initialize the database upon object creation

    def initialize_db(self):
        """Initializes the in-memory database with an admin user."""
        # Retrieve admin password from environment variable
        admin_password = os.getenv("ADMIN_PASSWORD")

        # Check if the password is provided in the environment variable
        if not admin_password:
            raise ValueError("Configuration error: Admin password not provided.")

        # Hash and store the admin password (username is 'admin')
        if "admin" not in self._users_db:
            self._users_db["admin"] = self.hash_password(admin_password)

    @staticmethod
    def hash_password(password):
        """Hashes a password using SHA-256."""
        if not password:
            raise ValueError("Password cannot be empty.")
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username, password):
        """Validates the username and password against the in-memory database."""
        if not username or not password:
            raise ValueError("Username and password cannot be empty.")

        hashed_password = self.hash_password(password)

        # Check if the username exists in the in-memory database and the password matches
        if self._users_db.get(username) == hashed_password:
            return True
        else:
            raise ValueError("Invalid username or password.")
