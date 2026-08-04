"""OpenAI provider implementation for Filtrify.

This provider connects Filtrify's provider-independent Artificial Intelligence
service to the OpenAI Responses Application Programming Interface.

AI means Artificial Intelligence.

API means Application Programming Interface. An API allows different software
systems to communicate with one another.
"""

from __future__ import annotations

import os
from typing import Any

from app.services.ai.ai_provider import (
    AIProvider,
    AIProviderRequest,
    AIProviderResponse,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment, misc]


class OpenAIProvider(AIProvider):
    """Generate Filtrify content using an OpenAI language model."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        default_model: str | None = None,
    ) -> None:
        """Initialize the OpenAI provider.

        Args:
            api_key:
                OpenAI Application Programming Interface key. When omitted,
                the provider reads the ``OPENAI_API_KEY`` environment variable.

            default_model:
                Model used when an individual request does not specify one.
                When omitted, the provider reads the ``OPENAI_MODEL``
                environment variable.

        Raises:
            ImportError:
                If the official OpenAI Python package is not installed.

            ValueError:
                If no Application Programming Interface key is available.
        """

        if OpenAI is None:
            raise ImportError(
                "The OpenAI Python package is not installed. "
                'Install it using: pip install openai'
            )

        resolved_api_key = (
            api_key
            or os.getenv("OPENAI_API_KEY")
        )

        if not resolved_api_key:
            raise ValueError(
                "No OpenAI Application Programming Interface key was found. "
                "Set the OPENAI_API_KEY environment variable."
            )

        self._default_model = (
            default_model
            or os.getenv("OPENAI_MODEL")
            or "gpt-5-mini"
        )

        self._client = OpenAI(
            api_key=resolved_api_key
        )

    @property
    def name(self) -> str:
        """Return the provider's unique internal name."""

        return "openai"

    @property
    def default_model(self) -> str:
        """Return the default OpenAI model."""

        return self._default_model

    def generate(
        self,
        request: AIProviderRequest,
    ) -> AIProviderResponse:
        """Generate content using the OpenAI Responses API.

        Args:
            request:
                Validated provider-independent generation request.

        Returns:
            A standardized ``AIProviderResponse``.

        Raises:
            ValueError:
                If the provider returns no generated text.

            RuntimeError:
                If the OpenAI request fails.
        """

        validated_request = self.validate_request(
            request
        )

        model_name = (
            validated_request.model
            or self.default_model
        )

        request_arguments: dict[str, Any] = {
            "model": model_name,
            "input": validated_request.prompt,
        }

        if validated_request.system_prompt:
            request_arguments["instructions"] = (
                validated_request.system_prompt
            )

        if (
            validated_request.maximum_output_tokens
            is not None
        ):
            request_arguments["max_output_tokens"] = (
                validated_request.maximum_output_tokens
            )

        try:
            response = self._client.responses.create(
                **request_arguments
            )
        except Exception as error:
            raise RuntimeError(
                "OpenAI could not generate the requested content. "
                f"Provider error: {error}"
            ) from error

        generated_content = str(
            getattr(
                response,
                "output_text",
                "",
            )
            or ""
        ).strip()

        if not generated_content:
            raise ValueError(
                "OpenAI returned an empty content response."
            )

        usage = getattr(
            response,
            "usage",
            None,
        )

        input_tokens = _read_usage_value(
            usage,
            "input_tokens",
        )

        output_tokens = _read_usage_value(
            usage,
            "output_tokens",
        )

        response_model = getattr(
            response,
            "model",
            None,
        )

        response_identifier = getattr(
            response,
            "id",
            None,
        )

        return AIProviderResponse(
            content=generated_content,
            provider_name=self.name,
            model_name=(
                str(response_model)
                if response_model
                else model_name
            ),
            success=True,
            message=(
                "Content generated successfully "
                "using OpenAI."
            ),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata={
                "response_id": response_identifier,
                "requested_model": model_name,
            },
        )


def _read_usage_value(
    usage: Any,
    attribute_name: str,
) -> int | None:
    """Read a token-usage value safely from an OpenAI response.

    Args:
        usage:
            Usage information returned by OpenAI.

        attribute_name:
            Name of the token value to retrieve.

    Returns:
        The token count when available, otherwise ``None``.
    """

    if usage is None:
        return None

    value = getattr(
        usage,
        attribute_name,
        None,
    )

    if isinstance(value, int):
        return value

    return None