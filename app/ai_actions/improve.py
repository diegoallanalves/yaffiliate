"""Improve Writing action for the Filtrify AI Workspace.

This action improves existing content while preserving its original meaning,
factual claims, and intended purpose.

AI means Artificial Intelligence.
"""

from __future__ import annotations

from app.ai_actions.ai_action import (
    AIActionContext,
)
from app.ai_actions.base_writing_action import (
    BaseWritingAction,
)


class ImproveWritingAction(BaseWritingAction):
    """Improve the clarity, flow, structure, and quality of content."""

    @property
    def key(self) -> str:
        """Return the unique registry key."""

        return "improve"

    @property
    def title(self) -> str:
        """Return the title displayed in the user interface."""

        return "Improve"

    @property
    def description(self) -> str:
        """Return a short explanation of the action."""

        return (
            "Improve clarity, flow, structure, and readability while "
            "preserving the original meaning."
        )

    @property
    def icon(self) -> str:
        """Return the icon displayed beside the action."""

        return "✨"

    @property
    def temperature(self) -> float:
        """Return the generation creativity level."""

        return 0.4

    @property
    def success_message_template(self) -> str:
        """Return the successful completion message template."""

        return (
            "The content was improved successfully "
            "using {provider_name}."
        )

    @property
    def provider_failure_message(self) -> str:
        """Return the default provider-failure message."""

        return (
            "The Artificial Intelligence provider "
            "could not improve the content."
        )

    @property
    def action_failure_message(self) -> str:
        """Return the action-level failure message."""

        return (
            "The Improve action could not be completed."
        )

    def build_system_prompt(self) -> str:
        """Build the high-level instructions sent to the AI provider."""

        return (
            "You are an expert conversion copywriter and content editor "
            "working inside Filtrify. Improve the supplied content without "
            "changing its original meaning. Preserve all factual information. "
            "Never invent product features, statistics, guarantees, reviews, "
            "testimonials, prices, results, or unsupported claims. Return only "
            "the finished improved content without commentary, explanations, "
            "headings such as 'Improved version', or quotation marks around "
            "the response."
        )

    def build_prompt(
        self,
        content: str,
        context: AIActionContext,
    ) -> str:
        """Build the content-improvement request."""

        instructions = [
            "Improve the following content.",
            "",
            "Requirements:",
            "- Preserve the original meaning and factual claims.",
            "- Improve clarity, flow, structure, and readability.",
            "- Remove unnecessary repetition.",
            "- Correct grammar, punctuation, and awkward wording.",
            "- Preserve useful headings, lists, and paragraph structure.",
            "- Do not invent statistics, testimonials, features, or claims.",
            "- Do not add explanations about the editing process.",
            "- Return only the improved content.",
        ]

        instructions.extend(
            self.build_context_requirements(
                context
            )
        )

        instructions.extend(
            [
                "",
                "Content to improve:",
                "",
                content,
            ]
        )

        return "\n".join(
            instructions
        )