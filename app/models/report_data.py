from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ReportData:
    """
    Complete Filtrify executive report.

    This model is renderer-agnostic.
    The same report can later be exported
    to PDF, HTML, Email or PowerPoint.
    """

    title: str

    subtitle: str

    generated_for: str

    executive_summary: str

    best_product: str

    business_consultant_summary: str

    commercial_strategy: str

    seo_strategy: str

    google_ads_strategy: str

    email_strategy: str

    landing_page_strategy: str

    risk_analysis: str

    final_verdict: str

    strengths: list[str] = field(default_factory=list)

    weaknesses: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)

    next_actions: list[str] = field(default_factory=list)

    confidence_score: float = 0.0