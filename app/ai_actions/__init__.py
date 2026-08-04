"""Artificial Intelligence actions available in Filtrify."""

from app.ai_actions.humanize import HumanizeAction

from app.ai_actions.ai_action import (
    AIAction,
    AIActionContext,
    AIActionResult,
)
from app.ai_actions.base_writing_action import (
    BaseWritingAction,
)
from app.ai_actions.expand import (
    ExpandAction,
)
from app.ai_actions.improve import (
    ImproveWritingAction,
)
from app.ai_actions.rewrite import (
    RewriteAction,
)
from app.ai_actions.shorten import (
    ShortenAction,
)


__all__ = [
    "AIAction",
    "AIActionContext",
    "AIActionResult",
    "BaseWritingAction",
    "ExpandAction",
    "HumanizeAction",
    "ImproveWritingAction",
    "RewriteAction",
    "ShortenAction",
]