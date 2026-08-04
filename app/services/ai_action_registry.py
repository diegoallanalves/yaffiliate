"""Registry for Filtrify Artificial Intelligence actions.

The registry stores available actions, prevents duplicate registrations,
groups actions by category, and provides a consistent way to execute them.
"""

from collections import defaultdict
from collections.abc import Iterable

from app.ai_actions.ai_action import (
    AIAction,
    AIActionContext,
    AIActionResult,
)


class AIActionRegistry:
    """Manage all registered Filtrify Artificial Intelligence actions."""

    def __init__(self) -> None:
        """Initialize an empty action registry."""

        self._actions: dict[str, AIAction] = {}

    def register(
        self,
        action: AIAction,
        *,
        replace: bool = False,
    ) -> None:
        """Register an Artificial Intelligence action.

        Args:
            action:
                Action instance to register.

            replace:
                Whether an existing action with the same key may be replaced.

        Raises:
            TypeError:
                If ``action`` does not inherit from ``AIAction``.

            ValueError:
                If the action key is empty or already registered.
        """

        if not isinstance(action, AIAction):
            raise TypeError(
                "Only AIAction instances can be registered."
            )

        normalized_key = self._normalize_key(action.key)

        if not normalized_key:
            raise ValueError("An Artificial Intelligence action key cannot be empty.")

        if normalized_key in self._actions and not replace:
            raise ValueError(
                f'An Artificial Intelligence action with the key '
                f'"{normalized_key}" is already registered.'
            )

        self._actions[normalized_key] = action

    def register_many(
        self,
        actions: Iterable[AIAction],
        *,
        replace: bool = False,
    ) -> None:
        """Register several actions.

        Args:
            actions:
                Iterable containing action instances.

            replace:
                Whether existing actions with matching keys may be replaced.
        """

        for action in actions:
            self.register(action, replace=replace)

    def unregister(self, key: str) -> AIAction:
        """Remove and return a registered action.

        Args:
            key:
                Unique action key.

        Returns:
            The removed action.

        Raises:
            KeyError:
                If the requested action is not registered.
        """

        normalized_key = self._normalize_key(key)

        if normalized_key not in self._actions:
            raise KeyError(
                f'Artificial Intelligence action "{normalized_key}" '
                "is not registered."
            )

        return self._actions.pop(normalized_key)

    def get(self, key: str) -> AIAction:
        """Return an action using its unique key.

        Args:
            key:
                Unique action key.

        Returns:
            The requested action.

        Raises:
            KeyError:
                If no action is registered under the supplied key.
        """

        normalized_key = self._normalize_key(key)

        try:
            return self._actions[normalized_key]
        except KeyError as error:
            available_keys = ", ".join(self.keys()) or "none"

            raise KeyError(
                f'Artificial Intelligence action "{normalized_key}" '
                f"was not found. Available actions: {available_keys}."
            ) from error

    def execute(
        self,
        key: str,
        content: str,
        context: AIActionContext | None = None,
    ) -> AIActionResult:
        """Execute a registered action.

        Args:
            key:
                Unique key of the action to execute.

            content:
                Existing content to process.

            context:
                Optional information such as tone, language, audience, and
                keywords.

        Returns:
            The result produced by the selected action.
        """

        action = self.get(key)
        validated_content = action.validate_content(content)
        validated_context = action.validate_context(context)

        return action.execute(
            content=validated_content,
            context=validated_context,
        )

    def all(self) -> tuple[AIAction, ...]:
        """Return all registered actions in registration order."""

        return tuple(self._actions.values())

    def keys(self) -> tuple[str, ...]:
        """Return all registered action keys."""

        return tuple(self._actions.keys())

    def categories(self) -> tuple[str, ...]:
        """Return the available action categories."""

        unique_categories = {
            action.category.strip()
            for action in self._actions.values()
            if action.category.strip()
        }

        return tuple(sorted(unique_categories, key=str.casefold))

    def grouped(self) -> dict[str, tuple[AIAction, ...]]:
        """Return registered actions grouped by category.

        Returns:
            Dictionary where each key is a category and each value is a tuple
            containing the actions assigned to that category.
        """

        grouped_actions: defaultdict[str, list[AIAction]] = defaultdict(list)

        for action in self._actions.values():
            category = action.category.strip() or "Other"
            grouped_actions[category].append(action)

        return {
            category: tuple(actions)
            for category, actions in sorted(
                grouped_actions.items(),
                key=lambda item: item[0].casefold(),
            )
        }

    def contains(self, key: str) -> bool:
        """Return whether an action key is registered."""

        normalized_key = self._normalize_key(key)
        return normalized_key in self._actions

    def clear(self) -> None:
        """Remove every registered action."""

        self._actions.clear()

    def __contains__(self, key: object) -> bool:
        """Support the ``key in registry`` syntax."""

        if not isinstance(key, str):
            return False

        return self.contains(key)

    def __len__(self) -> int:
        """Return the number of registered actions."""

        return len(self._actions)

    def __iter__(self):
        """Iterate through the registered actions."""

        return iter(self._actions.values())

    def __repr__(self) -> str:
        """Return a developer-friendly registry representation."""

        return (
            f"{self.__class__.__name__}("
            f"actions={len(self)}, "
            f"keys={list(self.keys())!r}"
            f")"
        )

    @staticmethod
    def _normalize_key(key: str) -> str:
        """Normalize an action key for consistent registry access.

        Args:
            key:
                Action key supplied by the caller.

        Returns:
            Lowercase key with surrounding whitespace removed.

        Raises:
            TypeError:
                If the supplied key is not a string.
        """

        if not isinstance(key, str):
            raise TypeError(
                "An Artificial Intelligence action key must be a string."
            )

        return key.strip().lower()


ai_action_registry = AIActionRegistry()