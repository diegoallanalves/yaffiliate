"""Admin access service for YAffiliate."""

from __future__ import annotations

import os

import streamlit as st


class AdminService:
    """Verify access to private YAffiliate owner tools."""

    @staticmethod
    def get_admin_user_id() -> str:
        """Return the configured YAffiliate admin user ID."""
        return str(
            os.getenv("ADMIN_USER_ID", "") or ""
        ).strip()

    @classmethod
    def is_admin(cls) -> bool:
        """Return True only for the configured admin user."""
        admin_user_id = cls.get_admin_user_id()

        current_user_id = str(
            st.session_state.get("auth_user_id", "") or ""
        ).strip()

        if not admin_user_id or not current_user_id:
            return False

        return current_user_id == admin_user_id