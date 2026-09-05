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
def test_activate_fixed_term_access_creates_30_day_pro_access():
    """A confirmed one-time payment should create fixed-term Pro access."""

    service = _service_without_database()

    class FakeResponse:
        data = [{"status": "active"}]

    class FakeTable:
        def __init__(self):
            self.record = None

        def upsert(self, record, on_conflict=None):
            self.record = record
            return self

        def execute(self):
            return FakeResponse()

    fake_table = FakeTable()

    class FakeAdminClient:
        def table(self, name):
            assert name == "subscriptions"
            return fake_table

    service.admin_client = FakeAdminClient()

    before = datetime.now(timezone.utc)

    result = service.activate_fixed_term_access(
        user_id="test-user",
        days=30,
        checkout_session_id="cs_test_pix",
        currency="BRL",
        country="br",
    )

    after = datetime.now(timezone.utc)

    assert result["status"] == "active"

    record = fake_table.record

    assert record["user_id"] == "test-user"
    assert record["plan"] == "pro"
    assert record["status"] == "active"
    assert record["access_type"] == "fixed_term"
    assert record["stripe_checkout_session_id"] == "cs_test_pix"
    assert record["currency"] == "brl"
    assert record["country"] == "BR"

    expiration = datetime.fromisoformat(
        record["access_expires_at"]
    )

    assert before + timedelta(days=30) <= expiration
    assert expiration <= after + timedelta(days=30)


def test_activate_fixed_term_access_rejects_invalid_duration():
    """Fixed-term access must always have a positive duration."""

    service = _service_without_database()

    try:
        service.activate_fixed_term_access(
            user_id="test-user",
            days=0,
        )
    except ValueError as exc:
        assert "greater than zero" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for invalid access duration."
        )