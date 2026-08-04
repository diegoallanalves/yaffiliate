"""Rewrite action for the Filtrify Artificial Intelligence Workspace.

This action rewrites existing content while preserving its original meaning,
facts, purpose, and important details.

AI means Artificial Intelligence.
"""

from __future__ import annotations

from app.ai_actions.ai_action import (
    AIActionContext,
)
from app.ai_actions.base_writing_action import (
    BaseWritingAction,
)


class RewriteAction(BaseWritingAction):
    """Rewrite content using clearer and more effective language."""

    @property
    def key(self) -> str:
        """Return the unique registry key."""

        return "rewrite"

    @property
    def title(self) -> str:
        """Return the action title displayed in the interface."""

        return "Rewrite"

    @property
    def description(self) -> str:
        """Return a short explanation of the action."""

        return (
            "Rewrite the content using fresh wording while preserving "
            "its meaning, facts, and intended purpose."
        )

    @property
    def icon(self) -> str:
        """Return the icon displayed beside the action."""

        return "✍️"

    @property
    def temperature(self) -> float:
        """Return the generation creativity level."""

        return 0.5

    @property
    def success_message_template(self) -> str:
        """Return the successful completion message template."""

        return (
            "The content was rewritten successfully "
            "using {provider_name}."
        )

    @property
    def provider_failure_message(self) -> str:
        """Return the default provider-failure message."""

        return (
            "The content could not be rewritten."
        )

    @property
    def action_failure_message(self) -> str:
        """Return the action-level failure message."""

        return (
            "The Rewrite action could not be completed."
        )

    def build_system_prompt(self) -> str:
        """Build the high-level provider instructions."""

        return (
            "You are an expert conversion copywriter and content editor "
            "working inside Filtrify. Rewrite the supplied content using "
            "fresh, natural, and effective language. Preserve its original "
            "meaning, factual information, purpose, and important details. "
            "Never invent product features, prices, statistics, guarantees, "
            "reviews, testimonials, results, or unsupported claims. Return "
            "only the completed rewritten content without explanations, "
            "commentary, quotation marks, or introductory labels."
        )

    def build_prompt(
        self,
        content: str,
        context: AIActionContext,
    ) -> str:
        """Build the rewriting request."""

        instructions = [
            "Rewrite the following content using fresh wording.",
            "",
            "Requirements:",
            "- Preserve the original meaning and factual claims.",
            "- Preserve all important information.",
            "- Use natural and engaging language.",
            "- Improve sentence variety and flow.",
            "- Remove unnecessary repetition.",
            "- Preserve useful headings, lists, and paragraph structure.",
            "- Do not shorten or expand the content significantly.",
            "- Do not invent features, evidence, statistics, or claims.",
            "- Do not explain the rewriting process.",
            "- Return only the rewritten content.",
        ]

        instructions.extend(
            self.build_context_requirements(
                context
            )
        )

        instructions.extend(
            [
                "",
                "Content to rewrite:",
                "",
                content,
            ]
        )

        return "\n".join(
            instructions
        )