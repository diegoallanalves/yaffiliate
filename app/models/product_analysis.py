from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ProductAnalysis:
    """
    Complete AI business analysis for one affiliate product.
    """

    headline: str

    commercial_potential: str

    seo_potential: str

    google_ads_potential: str

    email_marketing_potential: str

    landing_page_potential: str

    target_audience: list[str] = field(default_factory=list)

    strengths: list[str] = field(default_factory=list)

    weaknesses: list[str] = field(default_factory=list)

    recommendations: list[str] = field(default_factory=list)

    probability_of_success: float = 0.0

    confidence_score: float = 0.0