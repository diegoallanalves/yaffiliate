"""Currency formatting and reference-rate conversion helpers for YAffiliate.

Conversions are for reporting only; never overwrite original product amounts.
Rates are fetched from Frankfurter (ECB reference data), not live trading quotes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from functools import lru_cache
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.services.translation_service import get_language

SUPPORTED_CURRENCIES = ("BRL", "USD", "EUR", "GBP")
FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"


def get_default_currency(language: str | None = None) -> str:
    """Return the default display currency for a language."""
    language = language if language is not None else get_language()
    return "BRL" if language == "pt_BR" else "USD"


def format_currency(
    amount: float | int | Decimal | None,
    currency: str | None = None,
) -> str:
    """Format a value in its own currency, without converting it."""
    if amount is None:
        return "—"

    currency = (currency or get_default_currency()).upper()
    try:
        value = Decimal(str(amount))
        if not value.is_finite():
            return "—"
    except (InvalidOperation, ValueError, TypeError):
        return "—"

    if currency == "BRL":
        formatted = f"{value:,.2f}"
        formatted = formatted.replace(",", "#").replace(".", ",").replace("#", ".")
        return f"R$ {formatted}"

    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency)
    if symbol:
        return f"{symbol}{value:,.2f}"
    return f"{currency} {value:,.2f}"


@lru_cache(maxsize=32)
def _fetch_rate_for_day(source: str, target: str, utc_day: str) -> tuple[Decimal, str] | None:
    """Cache a reference rate per UTC day, per currency pair.

    The utc_day argument acts as a cache key; the provider supplies the actual
    published rate date, which can be older on weekends and holidays.
    """
    url = f"{FRANKFURTER_URL}?base={source}&symbols={target}"
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "YAffiliate/1.0"})
    try:
        with urlopen(request, timeout=8) as response:
            payload = json.load(response)
        rate = Decimal(str(payload["rates"][target]))
        published_date = str(payload["date"])
        if not rate.is_finite() or rate <= 0:
            return None
        datetime.strptime(published_date, "%Y-%m-%d")
        return rate, published_date
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, TypeError, InvalidOperation):
        return None


def get_exchange_rate(source_currency: str, target_currency: str) -> tuple[Decimal, str] | None:
    """Return (reference rate, published date), or None when unavailable.

    A same-currency conversion requires no network request.
    """
    source = str(source_currency or "").strip().upper()
    target = str(target_currency or "").strip().upper()
    if source not in SUPPORTED_CURRENCIES or target not in SUPPORTED_CURRENCIES:
        return None
    if source == target:
        return Decimal("1"), datetime.now(timezone.utc).date().isoformat()
    today = datetime.now(timezone.utc).date().isoformat()
    return _fetch_rate_for_day(source, target, today)


def convert_currency(
    amount: float | int | Decimal | None,
    source_currency: str,
    target_currency: str,
) -> Decimal | None:
    """Convert for display/reporting; return None if no trustworthy rate exists."""
    try:
        value = Decimal(str(amount))
        if not value.is_finite():
            return None
    except (InvalidOperation, ValueError, TypeError):
        return None
    rate_data = get_exchange_rate(source_currency, target_currency)
    if rate_data is None:
        return None
    rate, _published_date = rate_data
    return value * rate
