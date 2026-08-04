"""Load and register the Artificial Intelligence actions used by Filtrify.

This module provides one central place for registering the actions available
inside the Artificial Intelligence Workspace.
"""

from app.ai_actions import (
    ExpandAction,
    HumanizeAction,
    ImproveWritingAction,
    RewriteAction,
    ShortenAction,
)
from app.services.ai_action_registry import (
    AIActionRegistry,
    ai_action_registry,
)


def load_ai_actions(
    registry: AIActionRegistry | None = None,
    *,
    replace: bool = False,
) -> AIActionRegistry:
    """Register all available Artificial Intelligence actions.

    Args:
        registry:
            Registry that should receive the actions. When omitted, the shared
            application-level registry is used.

        replace:
            Whether existing actions with matching keys should be replaced.

    Returns:
        The registry containing all registered actions.
    """

    target_registry = registry or ai_action_registry

    target_registry.register_many(
        [
            ImproveWritingAction(),
            RewriteAction(),
            ExpandAction(),
            ShortenAction(),
            HumanizeAction(),
        ],
        replace=replace,
    )

    return target_registry


def ensure_ai_actions_loaded(
    registry: AIActionRegistry | None = None,
) -> AIActionRegistry:
    """Ensure that all available actions are registered exactly once.

    Args:
        registry:
            Registry that should contain the actions. When omitted, the shared
            application-level registry is used.

    Returns:
        The registry containing all available actions.
    """

    target_registry = registry or ai_action_registry

    actions = [
        ImproveWritingAction(),
        RewriteAction(),
        ExpandAction(),
        ShortenAction(),
        HumanizeAction(),
    ]

    for action in actions:
        if not target_registry.contains(action.key):
            target_registry.register(action)

    return target_registry