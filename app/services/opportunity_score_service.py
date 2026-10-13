
from __future__ import annotations

from dataclasses import dataclass, fields
from math import isfinite


@dataclass(slots=True)
class OpportunityFactors:
    """
    Product research inputs.

    None means the value is unknown.
    Zero means a confirmed value of zero.
    """

    commission_amount: float | None = None
    commission_percent: float | None = None
    search_volume: int | None = None
    competition_score: float | None = None
    estimated_cpc: float | None = None
    google_trend_score: float | None = None
    refund_rate: float | None = None
    gravity_score: float | None = None
    epc: float | None = None


class OpportunityScoreService:
    """
    Calculate a conservative opportunity score from known data.

    Score: 0 to 100.
    Coverage: percentage of scoring inputs with known values.

    Missing inputs earn no points, rather than being treated
    as confirmed zero values.

    This is a heuristic, not a prediction of actual sales.
    """

    MAX_SCORE = 100

    # The original scoring weights are preserved.
    WEIGHTS = {
        "commission_amount": 20,
        "commission_percent": 10,
        "search_volume": 20,
        "google_trend_score": 15,
        "competition_score": 15,
        "estimated_cpc": 10,
        "refund_rate": 10,
    }

    @staticmethod
    def _known(value: float | int | None) -> bool:
        """Check whether a metric contains a usable number."""
        if value is None:
            return False

        try:
            return isfinite(float(value))
        except (TypeError, ValueError, OverflowError):
            return False

    @staticmethod
    def _clamp(value: float, maximum: float) -> float:
        """Keep a positive metric within its expected range."""
        return min(max(float(value), 0.0), maximum)

    def calculate(
        self,
        factors: OpportunityFactors,
    ) -> float:
        """Return a conservative opportunity score (0-100)."""

        score = 0.0

        if self._known(factors.commission_amount):
            score += (
                self._clamp(factors.commission_amount, 300.0)
                / 300.0
                * 20
            )

        if self._known(factors.commission_percent):
            score += (
                self._clamp(factors.commission_percent, 100.0)
                / 100.0
                * 10
            )

        if self._known(factors.search_volume):
            score += (
                self._clamp(factors.search_volume, 10000.0)
                / 10000.0
                * 20
            )

        if self._known(factors.google_trend_score):
            score += (
                self._clamp(factors.google_trend_score, 100.0)
                / 100.0
                * 15
            )

        if self._known(factors.competition_score):
            score += (
                1.0
                - self._clamp(factors.competition_score, 100.0)
                / 100.0
            ) * 15

        if self._known(factors.estimated_cpc):
            score += (
                1.0
                - self._clamp(factors.estimated_cpc, 10.0)
                / 10.0
            ) * 10

        if self._known(factors.refund_rate):
            score += (
                1.0
                - self._clamp(factors.refund_rate, 100.0)
                / 100.0
            ) * 10

        return round(
            min(max(score, 0.0), self.MAX_SCORE),
            2,
        )

    def calculate_coverage(
        self,
        factors: OpportunityFactors,
    ) -> float:
        """
        Return the weighted percentage of available scoring data.

        Only the seven factors used by calculate() are counted.
        Gravity and EPC are not included because the existing
        scoring formula does not use them.
        """

        available_weight = sum(
            weight
            for field_name, weight in self.WEIGHTS.items()
            if self._known(getattr(factors, field_name))
        )

        total_weight = sum(self.WEIGHTS.values())

        if total_weight == 0:
            return 0.0

        return round(
            available_weight / total_weight * 100.0,
            2,
        )

    def calculate_details(
        self,
        factors: OpportunityFactors,
    ) -> dict:
        """
        Return score and coverage without changing calculate().

        This allows existing YAffiliate pages to continue
        calling calculate() exactly as before.
        """

        missing_factors = [
            field_name
            for field_name in self.WEIGHTS
            if not self._known(getattr(factors, field_name))
        ]

        return {
            "opportunity_score": self.calculate(factors),
            "data_coverage": self.calculate_coverage(factors),
            "missing_factors": missing_factors,
            "scoring_method": "Conservative weighted score",
        }
