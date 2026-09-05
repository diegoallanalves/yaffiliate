"""Tests for YAffiliate Pro subscription access rules."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.services.subscription_service import SubscriptionService


def _service_without_database() -> SubscriptionService:
    """Create the service without connecting to Supabase."""
    return SubscriptionService.__new__(SubscriptionService)


def test_active_subscription_is_pro():
    service = _service_without_database()

    subscription = {
        "plan": "pro",
        "status": "active",
        "access_type": "subscription",
    }

    with patch.object(
        service,
        "get_subscription",
        return_value=subscription,
    ):
        assert service.is_pro("test-user") is True


def test_future_fixed_term_access_is_pro():
    service = _service_without_database()

    future = datetime.now(timezone.utc) + timedelta(days=30)

    subscription = {
        "plan": "pro",
        "status": "active",
        "access_type": "fixed_term",
        "access_expires_at": future.isoformat(),
    }

    with patch.object(
        service,
        "get_subscription",
        return_value=subscription,
    ):
        assert service.is_pro("test-user") is True


def test_expired_fixed_term_access_is_not_pro():
    service = _service_without_database()

    past = datetime.now(timezone.utc) - timedelta(seconds=1)

    subscription = {
        "plan": "pro",
        "status": "active",
        "access_type": "fixed_term",
        "access_expires_at": past.isoformat(),
    }

    with patch.object(
        service,
        "get_subscription",
        return_value=subscription,
    ):
        assert service.is_pro("test-user") is False


def test_fixed_term_without_expiration_is_not_pro():
    service = _service_without_database()

    subscription = {
        "plan": "pro",
        "status": "active",
        "access_type": "fixed_term",
        "access_expires_at": None,
    }

    with patch.object(
        service,
        "get_subscription",
        return_value=subscription,
    ):
        assert service.is_pro("test-user") is False


def test_inactive_fixed_term_access_is_not_pro():
    service = _service_without_database()

    future = datetime.now(timezone.utc) + timedelta(days=30)

    subscription = {
        "plan": "pro",
        "status": "inactive",
        "access_type": "fixed_term",
        "access_expires_at": future.isoformat(),
    }

    with patch.object(
        service,
        "get_subscription",
        return_value=subscription,
    ):
        assert service.is_pro("test-user") is False