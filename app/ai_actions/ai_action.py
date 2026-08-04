"""Base definitions for Filtrify Artificial Intelligence actions.

An Artificial Intelligence action represents one transformation that can be
applied to content, such as improving, rewriting, expanding, or shortening it.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class AIActionContext:
    """Additional information supplied when an AI action is executed.

    Attributes:
        content_type:
            Type of content being edited, such as ``seo_article`` or
            ``landing_page``.

        language:
            Language in which the output should be generated.

        tone:
            Desired writing tone, such as professional, conversational,
            persuasive, or friendly.

        target_audience:
            Intended audience for the content.

        keywords:
            Search-engine keywords that may need to appear in the content.

        additional_instructions:
            Optional instructions entered by the user.

        metadata:
            Extra contextual values that future actions may require.
    """

    content_type: str | None = None
    language: str | None = None
    tone: str | None = None
    target_audience: str | None = None
    keywords: tuple[str, ...] = ()
    additional_instructions: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AIActionResult:
    """Result returned after an Artificial Intelligence action is executed.

    Attributes:
        original_content:
            Content supplied before the action was executed.

        generated_content:
            New content produced by the action.

        action_key:
            Unique key of the action that produced the result.

        action_title:
            Human-readable title of the action.

        success:
            Indicates whether the action completed successfully.

        message:
            Optional success, warning, or error message.

        metadata:
            Extra result information, such as model name, token counts,
            execution time, or version identifiers.
    """

    original_content: str
    generated_content: str
    action_key: str
    action_title: str
    success: bool = True
    message: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


class AIAction(ABC):
    """Abstract base class for every Filtrify Artificial Intelligence action.

    Each concrete action must provide:

    - A unique ``key`` used internally by the registry.
    - A user-facing ``title``.
    - A short ``description``.
    - An ``icon`` displayed by the interface.
    - A ``category`` used to group actions in the workspace.
    - An ``execute`` implementation.

    Concrete actions should not contain Streamlit interface code. Their
    responsibility is limited to validating input, preparing instructions,
    calling the appropriate service, and returning an ``AIActionResult``.
    """

    @property
    @abstractmethod
    def key(self) -> str:
        """Return the unique registry key for the action."""

    @property
    @abstractmethod
    def title(self) -> str:
        """Return the user-facing title of the action."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a short explanation of what the action does."""

    @property
    @abstractmethod
    def icon(self) -> str:
        """Return the icon displayed beside the action title."""

    @property
    def category(self) -> str:
        """Return the workspace category in which the action is displayed."""

        return "Writing"

    @property
    def requires_content(self) -> bool:
        """Return whether the action requires existing content."""

        return True

    @property
    def minimum_content_length(self) -> int:
        """Return the minimum accepted content length."""

        return 1

    def validate_content(self, content: str) -> str:
        """Validate and normalize content before action execution.

        Args:
            content:
                Existing editor content that will be transformed.

        Returns:
            The normalized content.

        Raises:
            TypeError:
                If ``content`` is not a string.

            ValueError:
                If required content is empty or shorter than the minimum
                accepted length.
        """

        if not isinstance(content, str):
            raise TypeError("AI action content must be provided as a string.")

        normalized_content = content.strip()

        if not self.requires_content:
            return normalized_content

        if not normalized_content:
            raise ValueError(
                f'The "{self.title}" action requires content to process.'
            )

        if len(normalized_content) < self.minimum_content_length:
            raise ValueError(
                f'The "{self.title}" action requires at least '
                f"{self.minimum_content_length} characters."
            )

        return normalized_content

    def validate_context(
        self,
        context: AIActionContext | None,
    ) -> AIActionContext:
        """Validate the optional action context.

        Args:
            context:
                Additional information used to perform the action.

        Returns:
            A valid ``AIActionContext`` instance.

        Raises:
            TypeError:
                If the supplied context has an unsupported type.
        """

        if context is None:
            return AIActionContext()

        if not isinstance(context, AIActionContext):
            raise TypeError(
                "AI action context must be an AIActionContext instance."
            )

        return context

    @abstractmethod
    def execute(
        self,
        content: str,
        context: AIActionContext | None = None,
    ) -> AIActionResult:
        """Execute the action and return its result.

        Concrete actions will implement this method when we connect the
        Artificial Intelligence service.

        Args:
            content:
                Existing content to transform.

            context:
                Optional information such as language, tone, audience, and
                keywords.

        Returns:
            An ``AIActionResult`` containing the original and generated
            content.
        """

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the action."""

        return (
            f"{self.__class__.__name__}("
            f"key={self.key!r}, "
            f"title={self.title!r}, "
            f"category={self.category!r}"
            f")"
        )