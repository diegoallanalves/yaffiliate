"""Currency formatting helpers for YAffiliate."""

from decimal import Decimal, InvalidOperation

from app.services.translation_service import get_language


def get_default_currency(language: str | None = None) -> str:
    """Return the default currency for the interface language."""
    language = language if language is not None else get_language()
    return "BRL" if language == "pt_BR" else "USD"


def format_currency(
    amount: float | int | Decimal | None,
    currency: str | None = None,
) -> str:
    """
    Format an amount in its specified currency.

    This function does not convert between currencies.
    """
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

    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = symbols.get(currency)
    if symbol:
        return f"{symbol}{value:,.2f}"

    return f"{currency} {value:,.2f}"