"""Reusable base class for Filtrify writing actions.

This module contains the shared execution behaviour used by writing actions
such as Improve, Rewrite, Expand, Shorten, and Humanize.

AI means Artificial Intelligence.

LLM means Large Language Model. An LLM is an Artificial Intelligence system
trained to understand and generate text.

A token is a small unit of text processed by an Artificial Intelligence model.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.ai_actions.ai_action import (
    AIAction,
    AIActionContext,
    AIActionResult,
)
from app.domain import (
    ArticleDocument,
)
from app.services.ai import (
    ai_service,
    configure_ai_service,
)
from app.services.article_document_output_formatter import (
    ArticleDocumentOutputFormatter,
)
from app.services.article_document_parser import (
    ArticleDocumentParser,
)
from app.services.article_document_response_parser import (
    ArticleDocumentResponseParser,
)


class BaseWritingAction(AIAction):
    """Provide shared execution behaviour for writing actions.

    Concrete writing actions only need to define their identity, prompts,
    temperature, and user-facing messages.

    This base class handles:

    - Content and context validation.
    - Artificial Intelligence service configuration.
    - Provider execution.
    - Output-token estimation.
    - Source-article parsing.
    - Artificial Intelligence response parsing.
    - Clean editor-text formatting.
    - Success-result construction.
    - Failure-result construction.
    - Diagnostic metadata.
    """

    @property
    def category(self) -> str:
        """Return the workspace category."""

        return "Writing"

    @property
    def minimum_content_length(self) -> int:
        """Return the minimum accepted content length."""

        return 10

    @property
    def temperature(self) -> float:
        """Return the generation creativity level.

        Lower values produce more predictable output.

        Higher values allow greater wording variation.
        """

        return 0.4

    @property
    def output_token_multiplier(self) -> float:
        """Return the output-size multiplier used for token estimation."""

        return 1.5

    @property
    def minimum_output_tokens(self) -> int:
        """Return the minimum requested output-token allowance."""

        return 500

    @property
    def maximum_output_tokens(self) -> int:
        """Return the maximum requested output-token allowance."""

        return 8_000

    @property
    def clean_generated_article(self) -> bool:
        """Return whether generated article content should be normalized.

        Actions can override this property if they intentionally need to
        preserve Markdown or another provider-specific output format.
        """

        return True

    @property
    @abstractmethod
    def success_message_template(self) -> str:
        """Return the successful completion message template.

        The template must contain a ``{provider_name}`` placeholder.
        """

    @property
    @abstractmethod
    def provider_failure_message(self) -> str:
        """Return the default provider-failure message."""

    @property
    @abstractmethod
    def action_failure_message(self) -> str:
        """Return the action-level failure message."""

    @abstractmethod
    def build_system_prompt(self) -> str:
        """Build the high-level instructions sent to the AI provider."""

    @abstractmethod
    def build_prompt(
        self,
        content: str,
        context: AIActionContext,
    ) -> str:
        """Build the action-specific content transformation prompt."""

    def execute(
        self,
        content: str,
        context: AIActionContext | None = None,
    ) -> AIActionResult:
        """Execute the writing action through the configured AI provider.

        Args:
            content:
                Existing content that should be transformed.

            context:
                Optional language, tone, audience, keyword, content-type,
                and user-instruction information.

        Returns:
            An ``AIActionResult`` containing either the generated content or
            diagnostic information explaining why generation failed.
        """

        validated_content = self.validate_content(
            content
        )

        validated_context = self.validate_context(
            context
        )

        source_document = self._prepare_source_document(
            content=validated_content,
            context=validated_context,
        )

        prompt = self.build_prompt(
            content=validated_content,
            context=validated_context,
        )

        try:
            self._ensure_ai_service_is_configured()

            response = ai_service.generate_text(
                prompt=prompt,
                system_prompt=self.build_system_prompt(),
                temperature=self.temperature,
                maximum_output_tokens=(
                    self._calculate_output_limit(
                        validated_content
                    )
                ),
                metadata=self._build_request_metadata(
                    validated_context
                ),
            )

            raw_generated_content = (
                response.content.strip()
            )

            if not response.success:
                return self._build_error_result(
                    original_content=validated_content,
                    prompt=prompt,
                    message=(
                        response.message
                        or self.provider_failure_message
                    ),
                    metadata={
                        "provider_name": (
                            response.provider_name
                        ),
                        "model_name": (
                            response.model_name
                        ),
                    },
                )

            if not raw_generated_content:
                return self._build_error_result(
                    original_content=validated_content,
                    prompt=prompt,
                    message=(
                        "The Artificial Intelligence provider "
                        "returned an empty response."
                    ),
                    metadata={
                        "provider_name": (
                            response.provider_name
                        ),
                        "model_name": (
                            response.model_name
                        ),
                    },
                )

            generated_content = (
                self._clean_generated_content(
                    generated_content=(
                        raw_generated_content
                    ),
                    source_document=source_document,
                )
            )

            if not generated_content.strip():
                return self._build_error_result(
                    original_content=validated_content,
                    prompt=prompt,
                    message=(
                        "The generated content became empty "
                        "after response processing."
                    ),
                    metadata={
                        "provider_name": (
                            response.provider_name
                        ),
                        "model_name": (
                            response.model_name
                        ),
                    },
                )

            return self._build_success_result(
                original_content=validated_content,
                generated_content=generated_content,
                prompt=prompt,
                response=response,
                source_document=source_document,
                raw_generated_content=(
                    raw_generated_content
                ),
            )

        except Exception as error:
            return self._build_error_result(
                original_content=validated_content,
                prompt=prompt,
                message=(
                    f"{self.action_failure_message} "
                    f"{error}"
                ),
                metadata={
                    "error_type": (
                        error.__class__.__name__
                    ),
                },
            )

    def _prepare_source_document(
        self,
        *,
        content: str,
        context: AIActionContext,
    ) -> ArticleDocument | None:
        """Convert editor content into a structured article when possible.

        Parsing failure is acceptable. Writing actions must continue working
        even when the supplied content is not recognized as a structured
        article.

        Args:
            content:
                Validated editor content.

            context:
                Current action context.

        Returns:
            A structured ``ArticleDocument`` when parsing succeeds.

            ``None`` when parsing is unsuccessful.
        """

        keywords = tuple(
            str(keyword).strip()
            for keyword in context.keywords
            if str(keyword).strip()
        )

        primary_keyword = (
            keywords[0]
            if keywords
            else ""
        )

        secondary_keywords = (
            keywords[1:]
            if len(keywords) > 1
            else ()
        )

        try:
            return ArticleDocumentParser().parse(
                content,
                primary_keyword=primary_keyword,
                secondary_keywords=(
                    secondary_keywords
                ),
                target_audience=(
                    context.target_audience
                    or ""
                ),
                tone=(
                    context.tone
                    or ""
                ),
                language=(
                    context.language
                    or "English"
                ),
                content_type=(
                    context.content_type
                    or "article"
                ),
                metadata={
                    "source": "ai_workspace",
                    "action_key": self.key,
                },
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

    def _clean_generated_content(
        self,
        *,
        generated_content: str,
        source_document: ArticleDocument | None,
    ) -> str:
        """Convert provider output into clean editor-friendly text.

        The response parser removes provider commentary, Markdown wrappers,
        heading markers, horizontal rules, and other presentation syntax.

        The output formatter then converts the structured response into plain
        text suitable for the Filtrify editor.

        If response parsing fails, the original provider output is returned so
        the action remains usable.

        Args:
            generated_content:
                Raw text returned by the Artificial Intelligence provider.

            source_document:
                Structured version of the original editor content, when
                available.

        Returns:
            Clean plain text or the original provider output as a fallback.
        """

        cleaned_generated_content = (
            generated_content.strip()
        )

        if not self.clean_generated_article:
            return cleaned_generated_content

        try:
            response_document = (
                ArticleDocumentResponseParser().parse(
                    cleaned_generated_content,
                    source_document=source_document,
                    metadata={
                        "action_key": self.key,
                        "response_cleaned": True,
                    },
                )
            )

            formatted_content = (
                ArticleDocumentOutputFormatter()
                .to_plain_text(
                    response_document
                )
            )

            if formatted_content.strip():
                return formatted_content.strip()

        except (
            TypeError,
            ValueError,
        ):
            pass

        return cleaned_generated_content

    def _build_request_metadata(
        self,
        context: AIActionContext,
    ) -> dict[str, Any]:
        """Build metadata sent to the Artificial Intelligence service."""

        return {
            "action_key": self.key,
            "action_title": self.title,
            "category": self.category,
            "content_type": (
                context.content_type
            ),
            "language": context.language,
            "tone": context.tone,
            "target_audience": (
                context.target_audience
            ),
            "keywords": tuple(
                str(keyword).strip()
                for keyword in context.keywords
                if str(keyword).strip()
            ),
        }

    def _build_success_result(
        self,
        *,
        original_content: str,
        generated_content: str,
        prompt: str,
        response: Any,
        source_document: ArticleDocument | None,
        raw_generated_content: str,
    ) -> AIActionResult:
        """Build a successful action result."""

        original_word_count = len(
            original_content.split()
        )

        generated_word_count = len(
            generated_content.split()
        )

        raw_generated_word_count = len(
            raw_generated_content.split()
        )

        return AIActionResult(
            original_content=original_content,
            generated_content=generated_content,
            action_key=self.key,
            action_title=self.title,
            success=True,
            message=(
                self.success_message_template.format(
                    provider_name=(
                        response.provider_name
                    )
                )
            ),
            metadata={
                "status": "completed",
                "prompt": prompt,
                "category": self.category,
                "provider_name": (
                    response.provider_name
                ),
                "model_name": (
                    response.model_name
                ),
                "input_tokens": (
                    response.input_tokens
                ),
                "output_tokens": (
                    response.output_tokens
                ),
                "source_document_parsed": (
                    source_document is not None
                ),
                "response_cleaned": (
                    generated_content
                    != raw_generated_content
                ),
                "original_word_count": (
                    original_word_count
                ),
                "raw_generated_word_count": (
                    raw_generated_word_count
                ),
                "generated_word_count": (
                    generated_word_count
                ),
                "word_count_change": (
                    generated_word_count
                    - original_word_count
                ),
                **dict(
                    response.metadata
                ),
            },
        )

    def _build_error_result(
        self,
        *,
        original_content: str,
        prompt: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> AIActionResult:
        """Build a consistent unsuccessful action result."""

        result_metadata: dict[str, Any] = {
            "status": "failed",
            "prompt": prompt,
            "category": self.category,
        }

        if metadata:
            result_metadata.update(
                metadata
            )

        return AIActionResult(
            original_content=original_content,
            generated_content=original_content,
            action_key=self.key,
            action_title=self.title,
            success=False,
            message=message,
            metadata=result_metadata,
        )

    def _calculate_output_limit(
        self,
        content: str,
    ) -> int:
        """Estimate a suitable output-token allowance."""

        approximate_input_tokens = max(
            1,
            len(content) // 4,
        )

        estimated_output_tokens = int(
            approximate_input_tokens
            * self.output_token_multiplier
        )

        return max(
            self.minimum_output_tokens,
            min(
                estimated_output_tokens,
                self.maximum_output_tokens,
            ),
        )

    @staticmethod
    def _ensure_ai_service_is_configured() -> None:
        """Configure the shared AI service when necessary.

        Raises:
            RuntimeError:
                If no Artificial Intelligence provider can be configured.
        """

        if ai_service.has_provider:
            return

        configured = configure_ai_service(
            ai_service
        )

        if not configured:
            raise RuntimeError(
                "No Artificial Intelligence provider is configured. "
                "Confirm that OPENAI_API_KEY exists in the local .env file."
            )

    @staticmethod
    def build_context_requirements(
        context: AIActionContext,
    ) -> list[str]:
        """Build reusable prompt requirements from the action context.

        Args:
            context:
                Optional language, tone, audience, keyword, content-type,
                and additional-instruction information.

        Returns:
            A list of prompt requirements ready to append to an action prompt.
        """

        requirements: list[str] = []

        if context.language:
            requirements.append(
                "- Write the result in this language: "
                f"{context.language}."
            )

        if context.tone:
            requirements.append(
                "- Use this writing tone: "
                f"{context.tone}."
            )

        if context.target_audience:
            requirements.append(
                "- Write for this target audience: "
                f"{context.target_audience}."
            )

        formatted_keywords = ", ".join(
            str(keyword).strip()
            for keyword in context.keywords
            if str(keyword).strip()
        )

        if formatted_keywords:
            requirements.append(
                "- Include these keywords naturally where relevant: "
                f"{formatted_keywords}."
            )

        if context.content_type:
            requirements.append(
                "- Treat the content as this type: "
                f"{context.content_type}."
            )

        if context.additional_instructions:
            requirements.append(
                "- Follow these additional instructions: "
                f"{context.additional_instructions}."
            )

        return requirements