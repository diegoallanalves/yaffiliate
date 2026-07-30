from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Recommendation:
    opportunity_score: float
    opportunity_level: str
    risk_level: str
    difficulty: str
    recommended_channel: str
    expected_roi: str
    recommended_budget: float
    reasoning: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)