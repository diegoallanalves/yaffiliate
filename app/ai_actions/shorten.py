"""Shorten action for the Filtrify Artificial Intelligence Workspace.

This action reduces the length of existing content while preserving its
essential meaning, factual claims, structure, and intended purpose.

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


class ShortenAction(BaseWritingAction):
    """Reduce content length while preserving its essential information."""

    @property
    def key(self) -> str:
        """Return the unique registry key."""

        return "shorten"

    @property
    def title(self) -> str:
        """Return the action title displayed in the interface."""

        return "Shorten"

    @property
    def description(self) -> str:
        """Return a short explanation of the action."""

        return (
            "Reduce the content to approximately 55–70% of its original "
            "length while preserving its key meaning and factual claims."
        )

    @property
    def icon(self) -> str:
        """Return the icon displayed beside the action."""

        return "✂️"

    @property
    def temperature(self) -> float:
        """Return the generation creativity level."""

        return 0.3

    @property
    def output_token_multiplier(self) -> float:
        """Allow enough output space for a concise complete result."""

        return 1.2

    @property
    def success_message_template(self) -> str:
        """Return the successful completion message template."""

        return (
            "The content was shortened successfully "
            "using {provider_name}."
        )

    @property
    def provider_failure_message(self) -> str:
        """Return the default provider-failure message."""

        return "The content could not be shortened."

    @property
    def action_failure_message(self) -> str:
        """Return the action-level failure message."""

        return "The Shorten action could not be completed."

    def build_system_prompt(self) -> str:
        """Build the high-level provider instructions."""

        return (
            "You are an expert content editor working inside Filtrify. "
            "Shorten the supplied content while preserving its essential "
            "meaning, factual information, purpose, section structure, "
            "important numerical values, and useful calls to action. Remove "
            "repetition, filler, unnecessary examples, and overly detailed "
            "explanations. Never invent, alter, or omit critical facts."
        )

    def build_prompt(
        self,
        content: str,
        context: AIActionContext,
    ) -> str:
        """Build the structured content-shortening prompt."""

        original_word_count = len(
            content.split()
        )

        minimum_target_words = max(
            80,
            int(original_word_count * 0.55),
        )

        maximum_target_words = max(
            minimum_target_words + 40,
            int(original_word_count * 0.70),
        )

        prompt_builder = AIPromptBuilder(
            role=(
                "You are a professional content editor and conversion "
                "copywriter working inside Filtrify."
            ),
            objective=(
                "Shorten the supplied content substantially while preserving "
                "its essential meaning, factual accuracy, usefulness, and "
                "reader-facing structure."
            ),
            content=content,
            content_label="Content to shorten",
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
                    "Preserve the title, main purpose, essential meaning, and "
                    "important factual claims."
                ),
                (
                    "Preserve all critical numerical values, prices, scores, "
                    "percentages, and commissions."
                ),
                (
                    "Remove repetition, filler, vague wording, and redundant "
                    "explanations."
                ),
                (
                    "Combine related ideas where doing so improves clarity."
                ),
                (
                    "Use shorter paragraphs and more direct sentences."
                ),
                (
                    "Preserve useful headings, conclusions, and calls to "
                    "action."
                ),
                (
                    "Do not reduce the content to bullet points unless the "
                    "source already uses them."
                ),
                (
                    "Do not remove warnings, limitations, risks, or important "
                    "buying considerations."
                ),
                (
                    "Keep the result natural, readable, and complete."
                ),
                (
                    "Return a meaningfully shorter version rather than a "
                    "simple rewrite."
                ),
            ]
        )

        prompt_builder.with_safety_rules(
            [
                (
                    "Do not invent, alter, round, or reinterpret factual "
                    "values."
                ),
                (
                    "Do not introduce new claims, product features, reviews, "
                    "testimonials, or evidence."
                ),
                (
                    "Do not remove information required to understand the "
                    "article's recommendation or risks."
                ),
                (
                    "Do not present assumptions as confirmed facts."
                ),
            ]
        )

        return prompt_builder.build()