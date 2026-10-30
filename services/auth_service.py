"""
services/auth_service.py
=========================
Simple session-based authentication. Passwords are hashed with Werkzeug's
PBKDF2 implementation (no plaintext, ever). This is intentionally not OAuth /
JWT -- for a self-hosted internal QA tool, server-side sessions are simpler,
safer by default, and sufficient.
"""

from __future__ import annotations

from typing import Optional

from werkzeug.security import check_password_hash, generate_password_hash

from database.db_manager import execute, fetch_one


class AuthService:
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[dict]:
        user = fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        if not user:
            return None
        if not check_password_hash(user["password_hash"], password):
            return None
        execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?", (user["id"],))
        return dict(user)

    @staticmethod
    def get_user(user_id: int) -> Optional[dict]:
        user = fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        return dict(user) if user else None

    @staticmethod
    def update_profile(user_id: int, full_name: str, email: str) -> None:
        execute("UPDATE users SET full_name = ?, email = ? WHERE id = ?", (full_name, email, user_id))

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
        user = fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        if not user:
            return False, "User not found."
        if not check_password_hash(user["password_hash"], old_password):
            return False, "Current password is incorrect."
        if len(new_password) < 8:
            return False, "New password must be at least 8 characters."
        execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), user_id),
        )
        return True, "Password updated successfully."
