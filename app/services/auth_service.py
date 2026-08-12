"""Supabase authentication service for YAffiliate."""

from __future__ import annotations

from typing import Any

from app.services.supabase_service import SupabaseService


class AuthService:
    """Handle YAffiliate user authentication with Supabase Auth."""

    def __init__(self) -> None:
        self.supabase = SupabaseService()
        self.client = self.supabase.client

    def sign_up(
        self,
        email: str,
        password: str,
    ) -> Any:
        """Create a new user with email and password."""

        cleaned_email = email.strip().lower()

        if not cleaned_email:
            raise ValueError("Email is required.")

        if not password:
            raise ValueError("Password is required.")

        return self.client.auth.sign_up(
            {
                "email": cleaned_email,
                "password": password,
            }
        )

    def sign_in(
        self,
        email: str,
        password: str,
    ) -> Any:
        """Sign in an existing user with email and password."""

        cleaned_email = email.strip().lower()

        if not cleaned_email:
            raise ValueError("Email is required.")

        if not password:
            raise ValueError("Password is required.")

        return self.client.auth.sign_in_with_password(
            {
                "email": cleaned_email,
                "password": password,
            }
        )

    def sign_out(self) -> None:
        """Sign out the currently authenticated user."""

        self.client.auth.sign_out()

    def get_current_user(self) -> Any | None:
        """Return the verified current Supabase user, if available."""

        try:
            response = self.client.auth.get_user()
        except Exception:
            return None

        return getattr(response, "user", None)

    def get_current_user_id(self) -> str | None:
        """Return the authenticated user's UUID."""

        user = self.get_current_user()

        if user is None:
            return None

        user_id = getattr(user, "id", None)

        return str(user_id) if user_id else None

    def get_current_user_email(self) -> str | None:
        """Return the authenticated user's email address."""

        user = self.get_current_user()

        if user is None:
            return None

        email = getattr(user, "email", None)

        return str(email) if email else None

    def is_authenticated(self) -> bool:
        """Return True when a verified authenticated user exists."""

        return self.get_current_user() is not None
