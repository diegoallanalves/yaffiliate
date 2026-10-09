"""Persistent authentication sessions for YAffiliate."""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import streamlit as st
from cryptography.fernet import Fernet, InvalidToken
from streamlit_cookies_controller import CookieController

from app.services.supabase_service import SupabaseService


COOKIE_NAME = "yaffiliate_session"
SESSION_DAYS = 30

logger = logging.getLogger(__name__)


class PersistentSessionService:
    """Manage persistent YAffiliate login sessions."""

    def __init__(self) -> None:
        self.supabase = SupabaseService()
        self.admin = self.supabase.admin_client

        key = str(
            os.getenv("AUTH_SESSION_ENCRYPTION_KEY")
            or st.secrets.get(
                "AUTH_SESSION_ENCRYPTION_KEY",
                ""
            )
        ).strip()

        if not key:
            raise ValueError(
                "AUTH_SESSION_ENCRYPTION_KEY is not configured."
            )

        self.fernet = Fernet(key.encode("utf-8"))

        self.cookies = CookieController(
            key="yaffiliate_cookie_controller"
        )

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    def _encrypt(self, value: str) -> str:
        return self.fernet.encrypt(
            value.encode("utf-8")
        ).decode("utf-8")

    def _decrypt(self, value: str) -> str:
        return self.fernet.decrypt(
            value.encode("utf-8")
        ).decode("utf-8")

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        result = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)

        return result

    def _delete_cookie(self) -> None:
        try:
            self.cookies.remove(COOKIE_NAME)
        except Exception:
            logger.warning(
                "Could not remove persistent cookie."
            )

    def _revoke_record(self, record_id: Any) -> None:
        try:
            (
                self.admin
                .table("auth_sessions")
                .update({
                    "revoked_at": self._now().isoformat()
                })
                .eq("id", record_id)
                .execute()
            )
        except Exception:
            logger.exception(
                "Could not revoke persistent session."
            )

    # -----------------------------------------------------
    # Create
    # -----------------------------------------------------

    def create(
        self,
        user_id: str,
        refresh_token: str,
    ) -> None:
        """Create a persistent login session."""

        user_id = str(user_id or "").strip()
        refresh_token = str(refresh_token or "").strip()

        if not user_id or not refresh_token:
            return

        browser_token = secrets.token_urlsafe(48)
        token_hash = self._hash_token(browser_token)

        expires_at = (
            self._now()
            + timedelta(days=SESSION_DAYS)
        )

        (
            self.admin
            .table("auth_sessions")
            .insert({
                "user_id": user_id,
                "session_token_hash": token_hash,
                "refresh_token": self._encrypt(
                    refresh_token
                ),
                "expires_at": expires_at.isoformat(),
            })
            .execute()
        )

        self.cookies.set(
            COOKIE_NAME,
            browser_token,
            max_age=SESSION_DAYS * 24 * 60 * 60,
        )

    # -----------------------------------------------------
    # Restore
    # -----------------------------------------------------

    def restore(self) -> bool:
        """Restore authentication from a browser cookie."""

        if st.session_state.get(
            "authenticated",
            False,
        ):
            return True

        # The browser cookie may not be available
        # during the first Streamlit execution.
        try:
            browser_token = self.cookies.get(COOKIE_NAME)
        except TypeError:
            # Cookie component has not initialized yet.
            return False

        if not browser_token:
            return False

        token_hash = self._hash_token(
            str(browser_token)
        )

        try:
            response = (
                self.admin
                .table("auth_sessions")
                .select(
                    "id,user_id,refresh_token,"
                    "expires_at,revoked_at"
                )
                .eq(
                    "session_token_hash",
                    token_hash,
                )
                .limit(1)
                .execute()
            )

        except Exception:
            logger.exception(
                "Persistent session lookup failed."
            )
            return False

        rows = response.data or []

        if not rows:
            self._delete_cookie()
            return False

        record = rows[0]

        if record.get("revoked_at"):
            self._delete_cookie()
            return False

        try:
            expires_at = self._parse_datetime(
                str(record["expires_at"])
            )
        except (ValueError, KeyError, TypeError):
            logger.exception(
                "Invalid persistent session expiry."
            )
            return False

        if expires_at <= self._now():
            self._revoke_record(record["id"])
            self._delete_cookie()
            return False

        try:
            refresh_token = self._decrypt(
                str(record["refresh_token"])
            )

        except (InvalidToken, ValueError):
            logger.warning(
                "Persistent session decryption failed."
            )
            return False

        try:
            auth_response = (
                self.supabase.client.auth.refresh_session(
                    refresh_token
                )
            )

        except Exception:
            # A temporary Supabase/network failure
            # should not revoke a valid session.
            logger.exception(
                "Supabase session refresh failed."
            )
            return False

        session = getattr(
            auth_response,
            "session",
            None,
        )

        user = getattr(
            auth_response,
            "user",
            None,
        )

        if session is None or user is None:
            logger.warning(
                "Supabase returned no authenticated session."
            )
            return False

        access_token = getattr(
            session,
            "access_token",
            None,
        )

        new_refresh_token = getattr(
            session,
            "refresh_token",
            None,
        )

        user_id = getattr(
            user,
            "id",
            None,
        )

        email = getattr(
            user,
            "email",
            None,
        )

        if (
            not access_token
            or not new_refresh_token
            or not user_id
        ):
            return False

        if str(user_id) != str(record["user_id"]):
            logger.error(
                "Persistent session user mismatch."
            )
            self._revoke_record(record["id"])
            self._delete_cookie()
            return False

        # Supabase refresh tokens rotate.
        # Save the newest encrypted token first.
        try:
            (
                self.admin
                .table("auth_sessions")
                .update({
                    "refresh_token": self._encrypt(
                        str(new_refresh_token)
                    )
                })
                .eq("id", record["id"])
                .execute()
            )

        except Exception:
            logger.exception(
                "Could not save rotated refresh token."
            )
            return False

        st.session_state["auth_user_id"] = str(user_id)
        st.session_state["auth_user_email"] = str(
            email or ""
        )
        st.session_state["supabase_access_token"] = str(
            access_token
        )
        st.session_state["supabase_refresh_token"] = str(
            new_refresh_token
        )
        st.session_state["authenticated"] = True

        return True

    # -----------------------------------------------------
    # Revoke
    # -----------------------------------------------------

    try:
        browser_token = self.cookies.get(COOKIE_NAME)
    except TypeError:
        logger.warning(
            "Cookie component not ready during logout."
        )
        browser_token = None

        if browser_token:
            token_hash = self._hash_token(
                str(browser_token)
            )

            (
                self.admin
                .table("auth_sessions")
                .update({
                    "revoked_at": self._now().isoformat()
                })
                .eq(
                    "session_token_hash",
                    token_hash,
                )
                .execute()
            )

        self._delete_cookie()