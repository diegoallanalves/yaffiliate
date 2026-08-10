"""Helpers for reading campaign records stored in Supabase."""

from __future__ import annotations

import json
from typing import Any


def decode_campaign_payload(value: object) -> dict[str, Any]:
    """Return a campaign payload as a dictionary."""
    if isinstance(value, dict):
        return value

    if not isinstance(value, str):
        raise ValueError("The saved campaign does not contain valid data.")

    try:
        loaded = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("The saved campaign contains invalid JSON.") from error

    if not isinstance(loaded, dict):
        raise ValueError("The saved campaign must contain a JSON object.")

    return loaded


def campaign_display_name(row: dict[str, Any]) -> str:
    """Return the best human-readable name for a saved campaign row."""
    try:
        payload = decode_campaign_payload(row.get("campaign"))
    except ValueError:
        payload = {}

    name = str(payload.get("campaign_name") or "").strip()
    if name:
        return name

    return str(row.get("product_name") or "Saved campaign")
