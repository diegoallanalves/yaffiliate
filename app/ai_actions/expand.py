"""Expand action for the Filtrify Artificial Intelligence Workspace.

This action expands existing content with useful detail while preserving its
original meaning, factual claims, purpose, and structure.

The action attempts to convert editor text into a structured ArticleDocument
before building the prompt. If parsing is unsuccessful, it safely falls back
to the original plain-text content.

AI means Artificial Intelligence.
"""

from __future__ import annotations

from app.ai_actions.ai_action import (
    AIActionContext,
)
from app.ai_actions.base_writing_action import (
    BaseWritingAction,
)
from app.prompts import (
    AIPromptBuilder,
)
from app.services.article_document_parser import (
    ArticleDocumentParser,
)


class ExpandAction(BaseWritingAction):
    """Expand content with additional relevant detail and explanation."""

    @property
    def key(self) -> str:
        """Return the unique registry key."""

        return "expand"

    @property
    def title(self) -> str:
        """Return the action title displayed in the interface."""

        return "Expand"

    @property
    def description(self) -> str:
        """Return a short explanation of the action."""

        return (
            "Expand the content to approximately 150–200% of its original "
            "length with relevant detail, explanation, and stronger flow."
        )

    @property
    def icon(self) -> str:
        """Return the icon displayed beside the action."""

        return "📈"

    @property
    def temperature(self) -> float:
        """Return the generation creativity level."""

        return 0.5

    @property
    def output_token_multiplier(self) -> float:
        """Allow the expanded result to be substantially longer."""

        return 3.0

    @property
    def minimum_output_tokens(self) -> int:
        """Return the minimum output-token allowance."""

        return 800

    @property
    def maximum_output_tokens(self) -> int:
        """Return the maximum output-token allowance."""

        return 10_000

    @property
    def success_message_template(self) -> str:
        """Return the successful completion message template."""

        return (
            "The content was expanded successfully "
            "using {provider_name}."
        )

    @property
    def provider_failure_message(self) -> str:
        """Return the default provider-failure message."""

        return "The content could not be expanded."

    @property
    def action_failure_message(self) -> str:
        """Return the action-level failure message."""

        return "The Expand action could not be completed."

    def build_system_prompt(self) -> str:
        """Build the high-level provider instructions."""

        return (
            "You are an expert conversion copywriter, content strategist, "
            "and editor working inside Filtrify. Expand supplied content with "
            "useful, relevant depth while preserving its original meaning, "
            "purpose, factual information, tone, section structure, and "
            "important claims. Develop thin sections, explain important "
            "ideas, strengthen transitions, and add practical context that "
            "can be safely derived from the supplied material. Never invent "
            "product features, prices, statistics, guarantees, reviews, "
            "testimonials, results, evidence, or unsupported claims."
        )

    def build_prompt(
        self,
        content: str,
        context: AIActionContext,
    ) -> str:
        """Build the structured content-expansion prompt.

        Args:
            content:
                Existing editor content that should be expanded.

            context:
                Language, tone, audience, keyword, content-type, and optional
                user-instruction information.

        Returns:
            A structured prompt produced by the shared prompt builder.
        """

        original_word_count = len(
            content.split()
        )

        minimum_target_words = max(
            original_word_count + 100,
            int(original_word_count * 1.5),
        )

        maximum_target_words = max(
            minimum_target_words + 100,
            int(original_word_count * 2.0),
        )

        prompt_content, content_label = (
            self._prepare_prompt_content(
                content=content,
                context=context,
            )
        )

        prompt_builder = AIPromptBuilder(
            role=(
                "You are a professional content strategist, conversion "
                "copywriter, and editor working inside Filtrify."
            ),
            objective=(
                "Expand the supplied article substantially. Increase its "
                "depth, usefulness, clarity, and explanatory value without "
                "changing its purpose or presenting unsupported information."
            ),
            content=prompt_content,
            content_label=content_label,
        )

        prompt_builder.with_context(
            context
        )

        prompt_builder.with_word_target(
            minimum_words=minimum_target_words,
            maximum_words=maximum_target_words,
        )

        prompt_builder.with_requirements(
            [
                (
                    "Preserve the original title, purpose, meaning, and "
                    "factual claims."
                ),
                (
                    "Preserve all important information from the source "
                    "article."
                ),
                (
                    "Use the labelled article structure to understand the "
                    "purpose of each section."
                ),
                (
                    "Expand every thin, brief, or underdeveloped article "
                    "section."
                ),
                (
                    "Add useful explanation and relevant practical context."
                ),
                (
                    "Explain why important points matter to the intended "
                    "reader."
                ),
                (
                    "Improve transitions between sections, paragraphs, and "
                    "ideas."
                ),
                (
                    "Develop short paragraphs into clearer and more complete "
                    "explanations."
                ),
                (
                    "Preserve useful headings, lists, paragraph structure, "
                    "frequently asked questions, conclusions, and calls to "
                    "action."
                ),
                (
                    "Do not output internal labels such as Section type, "
                    "Article context, Content type, or Primary keyword."
                ),
                (
                    "Return a natural, reader-facing article rather than a "
                    "description of the article structure."
                ),
                (
                    "Keep the expanded article focused on its original "
                    "purpose."
                ),
                (
                    "Make the final version clearly longer and more detailed "
                    "than the source."
                ),
                (
                    "Do not merely rewrite the source using different "
                    "wording."
                ),
                (
                    "Avoid filler, vague statements, and unnecessary "
                    "repetition."
                ),
            ]
        )

        prompt_builder.with_safety_rules(
            [
                (
                    "Do not invent product features, prices, discounts, "
                    "statistics, guarantees, or performance results."
                ),
                (
                    "Do not invent reviews, testimonials, customer "
                    "experiences, or evidence."
                ),
                (
                    "Do not present assumptions, estimates, or possibilities "
                    "as confirmed facts."
                ),
                (
                    "When additional verified facts are unavailable, expand "
                    "through explanation, implications, considerations, and "
                    "reader guidance instead of invented information."
                ),
                (
                    "Preserve numerical values and factual details exactly "
                    "unless correction is explicitly requested."
                ),
            ]
        )

        return prompt_builder.build()

    def _prepare_prompt_content(
        self,
        *,
        content: str,
        context: AIActionContext,
    ) -> tuple[str, str]:
        """Convert editor content into structured prompt content.

        The parser is intentionally used behind a safe fallback. A parsing
        problem must not prevent the Artificial Intelligence action from
        working.

        Args:
            content:
                Original plain-text editor content.

            context:
                Current Artificial Intelligence action context.

        Returns:
            A tuple containing the prompt content and its section label.
        """

        keywords = tuple(
            keyword.strip()
            for keyword in context.keywords
            if isinstance(
                keyword,
                str,
            )
            and keyword.strip()
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
            document = ArticleDocumentParser().parse(
                content,
                primary_keyword=primary_keyword,
                secondary_keywords=secondary_keywords,
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
                    "action": self.key,
                },
            )
        except (
            TypeError,
            ValueError,
        ):
            return (
                content,
                "Content to expand",
            )

        if document.is_empty:
            return (
                content,
                "Content to expand",
            )

        structured_content = (
            document.to_prompt_text()
        )

        if not structured_content.strip():
            return (
                content,
                "Content to expand",
            )

        return (
            structured_content,
            "Structured article to expand",
        )