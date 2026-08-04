"""Artificial Intelligence services available in Filtrify.

This package exposes Filtrify's provider-independent Artificial Intelligence
architecture.

It also includes a backward-compatible ``generate_text`` function so older
pages can continue working while they are gradually migrated to the new
``AIService`` interface.

AI means Artificial Intelligence.

API means Application Programming Interface.
"""

from __future__ import annotations

from typing import Any, Mapping

from app.services.ai.ai_configuration import (
    configure_ai_service,
)
from app.services.ai.ai_provider import (
    AIProvider,
    AIProviderRequest,
    AIProviderResponse,
)
from app.services.ai.ai_service import (
    AIService,
    AIServiceRequest,
    AIServiceResponse,
    ai_service,
)
from app.services.ai.openai_provider import (
    OpenAIProvider,
)


def generate_text(
    system_prompt: str,
    prompt: str,
    *,
    model: str | None = None,
    temperature: float = 0.4,
    maximum_output_tokens: int | None = 2_000,
    metadata: Mapping[str, Any] | None = None,
) -> str:
    """Generate text through Filtrify's central AI service.

    This function preserves compatibility with older Filtrify pages that use:

    ``generate_text(system_prompt, prompt)``

    Newer code should generally use ``ai_service.generate_text`` directly
    because it returns a complete ``AIServiceResponse``.

    Args:
        system_prompt:
            Higher-level instructions describing how the model should behave.

        prompt:
            Main request and source content sent to the model.

        model:
            Optional model name. When omitted, the configured provider's
            default model is used.

        temperature:
            Controls how consistent or creative the generated response should
            be. Lower values usually produce more predictable results.

        maximum_output_tokens:
            Maximum number of tokens the provider may generate. A token is a
            small unit of text processed by an Artificial Intelligence model.

        metadata:
            Optional information associated with the request.

    Returns:
        Generated text returned by the configured provider.

    Raises:
        RuntimeError:
            If no Artificial Intelligence provider can be configured or the
            generation request fails.
    """

    if not ai_service.has_provider:
        configured = configure_ai_service(
            ai_service
        )

        if not configured:
            raise RuntimeError(
                "No Artificial Intelligence provider is configured. "
                "Confirm that OPENAI_API_KEY exists in the local .env file."
            )

    response = ai_service.generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        maximum_output_tokens=maximum_output_tokens,
        metadata=metadata or {},
    )

    if not response.success:
        raise RuntimeError(
            response.message
            or "The Artificial Intelligence request was unsuccessful."
        )

    generated_content = response.content.strip()

    if not generated_content:
        raise RuntimeError(
            "The Artificial Intelligence provider returned an empty response."
        )

    return generated_content


__all__ = [
    "AIProvider",
    "AIProviderRequest",
    "AIProviderResponse",
    "AIService",
    "AIServiceRequest",
    "AIServiceResponse",
    "OpenAIProvider",
    "ai_service",
    "configure_ai_service",
    "generate_text",
]