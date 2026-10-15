from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OpportunityFactors:
    commission_amount: float
    commission_percent: float
    search_volume: int
    competition_score: float
    estimated_cpc: float
    google_trend_score: float
    refund_rate: float
    gravity_score: float | None = None
    epc: float | None = None


class OpportunityScoreService:
    """
    Calculates a standardized Opportunity Score (0–100).

    This is the core intelligence engine of Filtrify.

    In future versions this service will include:

    - Google Trends
    - Reddit popularity
    - Facebook Ads
    - YouTube demand
    - AI market sentiment
    - Historical conversions
    - Seasonality
    - Machine Learning
    """

    MAX_SCORE = 100

    def calculate(
        self,
        factors: OpportunityFactors,
    ) -> float:

        score = 0

        # Commission Amount
        score += min(factors.commission_amount / 300, 1) * 20

        # Commission %
        score += min(factors.commission_percent / 100, 1) * 10

        # Search Volume
        score += min(factors.search_volume / 10000, 1) * 20

        # Trend
        score += min(factors.google_trend_score / 100, 1) * 15

        # Competition
        score += max(
            0,
            1 - (factors.competition_score / 100)
        ) * 15

        # CPC
        score += max(
            0,
            1 - (factors.estimated_cpc / 10)
        ) * 10

        # Refund Rate
        score += max(
            0,
            1 - (factors.refund_rate / 100)
        ) * 10

        return round(
            min(score, self.MAX_SCORE),
            2,
        )