"""Artificial Intelligence configuration for Filtrify.

This module loads environment variables and configures the shared
Artificial Intelligence service.

AI means Artificial Intelligence.

API means Application Programming Interface.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from app.services.ai.ai_service import AIService
from app.services.ai.openai_provider import OpenAIProvider


def configure_ai_service(
    service: AIService,
) -> bool:
    """Configure an Artificial Intelligence service.

    Args:
        service:
            Filtrify Artificial Intelligence service that should receive
            the configured provider.

    Returns:
        True when the OpenAI provider was configured.

        False when the OpenAI API key was not found.
    """

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return False

    default_model = (
        os.getenv("OPENAI_MODEL")
        or "gpt-4.1-mini"
    )

    provider = OpenAIProvider(
        api_key=api_key,
        default_model=default_model,
    )

    service.set_provider(provider)

    return True