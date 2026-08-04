"""Humanize action for the Filtrify Artificial Intelligence Workspace.

This action rewrites content so it sounds more natural and human while
preserving its original meaning, factual claims, structure, and purpose.

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


class HumanizeAction(BaseWritingAction):
    """Make content sound natural, varied, and professionally human-written."""

    @property
    def key(self) -> str:
        """Return the unique registry key."""

        return "humanize"

    @property
    def title(self) -> str:
        """Return the action title displayed in the interface."""

        return "Humanize"

    @property
    def description(self) -> str:
        """Return a short explanation of the action."""

        return (
            "Make the content sound naturally written by an experienced "
            "human while preserving its facts, meaning, and structure."
        )

    @property
    def icon(self) -> str:
        """Return the icon displayed beside the action."""

        return "👤"

    @property
    def temperature(self) -> float:
        """Return the generation creativity level."""

        return 0.6

    @property
    def output_token_multiplier(self) -> float:
        """Allow enough space to preserve the original content length."""

        return 1.6

    @property
    def minimum_output_tokens(self) -> int:
        """Return the minimum output-token allowance."""

        return 700

    @property
    def success_message_template(self) -> str:
        """Return the successful completion message template."""

        return (
            "The content was humanized successfully "
            "using {provider_name}."
        )

    @property
    def provider_failure_message(self) -> str:
        """Return the default provider-failure message."""

        return "The content could not be humanized."

    @property
    def action_failure_message(self) -> str:
        """Return the action-level failure message."""

        return "The Humanize action could not be completed."

    def build_system_prompt(self) -> str:
        """Build the high-level provider instructions."""

        return (
            "You are an experienced human editor and conversion copywriter "
            "working inside Filtrify. Rewrite the supplied content so it "
            "sounds natural, thoughtful, varied, and professionally written. "
            "Preserve the original meaning, factual information, numerical "
            "values, structure, purpose, and important claims. Remove robotic "
            "phrasing, repetitive sentence patterns, generic transitions, "
            "and unnatural wording. Never invent product features, prices, "
            "statistics, guarantees, reviews, testimonials, results, or "
            "unsupported claims. Return only the completed content."
        )

    def build_prompt(
        self,
        content: str,
        context: AIActionContext,
    ) -> str:
        """Build the structured humanization prompt.

        Args:
            content:
                Existing content that should be humanized.

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
            80,
            int(original_word_count * 0.90),
        )

        maximum_target_words = max(
            minimum_target_words + 40,
            int(original_word_count * 1.10),
        )

        prompt_builder = AIPromptBuilder(
            role=(
                "You are an experienced human editor, content strategist, "
                "and conversion copywriter working inside Filtrify."
            ),
            objective=(
                "Rewrite the supplied content so it reads naturally and "
                "professionally, with the rhythm, clarity, and variation of "
                "experienced human writing."
            ),
            content=content,
            content_label="Content to humanize",
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
                    "Preserve the original meaning, purpose, factual claims, "
                    "and important details."
                ),
                (
                    "Preserve all prices, percentages, scores, commissions, "
                    "statistics, and other numerical values exactly."
                ),
                (
                    "Keep the same approximate length unless clearer wording "
                    "requires a small change."
                ),
                (
                    "Use varied sentence lengths and natural paragraph flow."
                ),
                (
                    "Replace robotic, repetitive, or formulaic phrasing with "
                    "natural human wording."
                ),
                (
                    "Remove generic transitions and predictable Artificial "
                    "Intelligence-style expressions."
                ),
                (
                    "Use clear and specific language instead of vague or "
                    "inflated wording."
                ),
                (
                    "Improve rhythm, readability, and sentence variety."
                ),
                (
                    "Preserve useful headings, lists, conclusions, and calls "
                    "to action."
                ),
                (
                    "Keep Search Engine Optimization keywords natural and "
                    "avoid keyword stuffing."
                ),
                (
                    "Do not make the writing excessively casual unless the "
                    "requested tone requires it."
                ),
                (
                    "Return a complete polished version rather than comments "
                    "about what should be changed."
                ),
            ]
        )

        prompt_builder.with_safety_rules(
            [
                (
                    "Do not invent product features, benefits, prices, "
                    "discounts, guarantees, or performance results."
                ),
                (
                    "Do not invent reviews, testimonials, customer "
                    "experiences, or evidence."
                ),
                (
                    "Do not alter numerical values or factual claims."
                ),
                (
                    "Do not present assumptions, estimates, or possibilities "
                    "as confirmed facts."
                ),
                (
                    "Do not add personal experiences or first-person claims "
                    "that are not present in the source."
                ),
            ]
        )

        return prompt_builder.build()