"""Reusable prompt builder for Filtrify Artificial Intelligence actions.

This module converts structured instructions and content context into a clear,
consistent prompt that can be used by Improve, Rewrite, Expand, Shorten,
Humanize, Search Engine Optimization, and future actions.

AI means Artificial Intelligence.

SEO means Search Engine Optimization.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.ai_actions.ai_action import (
    AIActionContext,
)


class AIPromptBuilder:
    """Build structured prompts for Filtrify Artificial Intelligence actions.

    The builder separates prompts into clearly labelled sections:

    - Role
    - Objective
    - Content context
    - Length target
    - Requirements
    - Safety rules
    - User instructions
    - Source content

    This makes prompts easier to maintain and easier for an Artificial
    Intelligence model to follow consistently.
    """

    def __init__(
        self,
        *,
        role: str,
        objective: str,
        content: str,
        content_label: str = "Source content",
    ) -> None:
        """Initialize the prompt builder.

        Args:
            role:
                Professional role the Artificial Intelligence model should
                perform.

            objective:
                Main transformation the model should complete.

            content:
                Existing content supplied to the action.

            content_label:
                Heading displayed immediately before the source content.
        """

        self._role = self._clean_required_text(
            role,
            field_name="role",
        )

        self._objective = self._clean_required_text(
            objective,
            field_name="objective",
        )

        self._content = self._clean_required_text(
            content,
            field_name="content",
        )

        self._content_label = self._clean_required_text(
            content_label,
            field_name="content_label",
        )

        self._context: AIActionContext | None = None
        self._requirements: list[str] = []
        self._safety_rules: list[str] = []
        self._minimum_words: int | None = None
        self._maximum_words: int | None = None

    def with_context(
        self,
        context: AIActionContext,
    ) -> AIPromptBuilder:
        """Attach action context to the prompt.

        Args:
            context:
                Language, tone, audience, keyword, content-type, and optional
                user-instruction information.

        Returns:
            The current builder, allowing chained method calls.
        """

        if not isinstance(
            context,
            AIActionContext,
        ):
            raise TypeError(
                "Prompt context must be an AIActionContext instance."
            )

        self._context = context

        return self

    def with_requirements(
        self,
        requirements: Iterable[str],
    ) -> AIPromptBuilder:
        """Add action-specific requirements.

        Args:
            requirements:
                Rules describing how the content should be transformed.

        Returns:
            The current builder, allowing chained method calls.
        """

        self._requirements.extend(
            self._normalize_list(
                requirements
            )
        )

        return self

    def with_safety_rules(
        self,
        safety_rules: Iterable[str],
    ) -> AIPromptBuilder:
        """Add factual and content-safety rules.

        Args:
            safety_rules:
                Rules preventing unsupported claims or invented information.

        Returns:
            The current builder, allowing chained method calls.
        """

        self._safety_rules.extend(
            self._normalize_list(
                safety_rules
            )
        )

        return self

    def with_word_target(
        self,
        *,
        minimum_words: int,
        maximum_words: int,
    ) -> AIPromptBuilder:
        """Add a measurable output-length target.

        Args:
            minimum_words:
                Minimum desired output word count.

            maximum_words:
                Maximum desired output word count.

        Returns:
            The current builder, allowing chained method calls.

        Raises:
            ValueError:
                If either value is invalid or the maximum is lower than the
                minimum.
        """

        if minimum_words < 1:
            raise ValueError(
                "Minimum target words must be greater than zero."
            )

        if maximum_words < minimum_words:
            raise ValueError(
                "Maximum target words cannot be lower than "
                "minimum target words."
            )

        self._minimum_words = minimum_words
        self._maximum_words = maximum_words

        return self

    def build(self) -> str:
        """Build the complete structured prompt.

        Returns:
            A formatted prompt ready to send to an Artificial Intelligence
            provider.
        """

        sections = [
            self._build_section(
                "ROLE",
                [
                    self._role,
                ],
            ),
            self._build_section(
                "OBJECTIVE",
                [
                    self._objective,
                ],
            ),
        ]

        context_lines = self._build_context_lines()

        if context_lines:
            sections.append(
                self._build_section(
                    "CONTENT CONTEXT",
                    context_lines,
                )
            )

        length_lines = self._build_length_lines()

        if length_lines:
            sections.append(
                self._build_section(
                    "LENGTH TARGET",
                    length_lines,
                )
            )

        if self._requirements:
            sections.append(
                self._build_bullet_section(
                    "REQUIREMENTS",
                    self._requirements,
                )
            )

        if self._safety_rules:
            sections.append(
                self._build_bullet_section(
                    "FACTUAL AND SAFETY RULES",
                    self._safety_rules,
                )
            )

        user_instruction_lines = (
            self._build_user_instruction_lines()
        )

        if user_instruction_lines:
            sections.append(
                self._build_section(
                    "ADDITIONAL USER INSTRUCTIONS",
                    user_instruction_lines,
                )
            )

        sections.append(
            self._build_section(
                "OUTPUT RULE",
                [
                    (
                        "Return only the completed content. Do not include "
                        "analysis, commentary, introductory labels, quotation "
                        "marks around the answer, or explanations of the "
                        "editing process."
                    ),
                ],
            )
        )

        sections.append(
            self._build_section(
                self._content_label.upper(),
                [
                    self._content,
                ],
            )
        )

        return "\n\n".join(
            sections
        ).strip()

    def _build_context_lines(
        self,
    ) -> list[str]:
        """Build context lines from the attached action context."""

        if self._context is None:
            return []

        context_lines: list[str] = []

        if self._context.content_type:
            context_lines.append(
                "Content type: "
                f"{self._context.content_type}"
            )

        if self._context.language:
            context_lines.append(
                "Output language: "
                f"{self._context.language}"
            )

        if self._context.tone:
            context_lines.append(
                "Writing tone: "
                f"{self._context.tone}"
            )

        if self._context.target_audience:
            context_lines.append(
                "Target audience: "
                f"{self._context.target_audience}"
            )

        formatted_keywords = ", ".join(
            str(keyword).strip()
            for keyword in self._context.keywords
            if str(keyword).strip()
        )

        if formatted_keywords:
            context_lines.append(
                "Target keywords: "
                f"{formatted_keywords}"
            )

        return context_lines

    def _build_length_lines(
        self,
    ) -> list[str]:
        """Build measurable word-count instructions."""

        if (
            self._minimum_words is None
            or self._maximum_words is None
        ):
            return []

        original_word_count = len(
            self._content.split()
        )

        return [
            (
                "Original length: approximately "
                f"{original_word_count:,} words."
            ),
            (
                "Desired output length: approximately "
                f"{self._minimum_words:,}–"
                f"{self._maximum_words:,} words."
            ),
            (
                "The final result should meaningfully follow this target "
                "without using filler or unnecessary repetition."
            ),
        ]

    def _build_user_instruction_lines(
        self,
    ) -> list[str]:
        """Return optional instructions entered by the user."""

        if self._context is None:
            return []

        additional_instructions = (
            self._context.additional_instructions
        )

        if not additional_instructions:
            return []

        cleaned_instructions = (
            additional_instructions.strip()
        )

        if not cleaned_instructions:
            return []

        return [
            cleaned_instructions,
        ]

    @staticmethod
    def _build_section(
        heading: str,
        lines: Iterable[str],
    ) -> str:
        """Build a plain-text prompt section."""

        cleaned_lines = [
            str(line).strip()
            for line in lines
            if str(line).strip()
        ]

        return "\n".join(
            [
                heading,
                *cleaned_lines,
            ]
        )

    @staticmethod
    def _build_bullet_section(
        heading: str,
        items: Iterable[str],
    ) -> str:
        """Build a prompt section containing bullet-point requirements."""

        cleaned_items = [
            str(item).strip().lstrip("-").strip()
            for item in items
            if str(item).strip()
        ]

        bullet_lines = [
            f"- {item}"
            for item in cleaned_items
        ]

        return "\n".join(
            [
                heading,
                *bullet_lines,
            ]
        )

    @staticmethod
    def _normalize_list(
        values: Iterable[str],
    ) -> list[str]:
        """Normalize a sequence of prompt rules."""

        return [
            str(value).strip()
            for value in values
            if str(value).strip()
        ]

    @staticmethod
    def _clean_required_text(
        value: str,
        *,
        field_name: str,
    ) -> str:
        """Validate and normalize required prompt text."""

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"Prompt {field_name} must be a string."
            )

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                f"Prompt {field_name} cannot be empty."
            )

        return cleaned_value