from __future__ import annotations

from typing import Any


class TrendAnalysisService:
    """
    Explains how a product's market metrics changed between
    the first and latest historical snapshots.
    """

    def analyse(
        self,
        timeline: dict[str, Any],
    ) -> dict[str, Any]:
        history = timeline.get("history") or []

        if len(history) < 2:
            return {
                "status": "Insufficient history",
                "headline": (
                    "At least two snapshots are required "
                    "before Filtrify can analyse a trend."
                ),
                "summary": (
                    "Create another historical snapshot for this product "
                    "to compare changes over time."
                ),
                "changes": [],
                "recommendation": (
                    "Continue collecting market data before changing strategy."
                ),
            }

        first = history[0]
        latest = history[-1]

        score_change = self._difference(
            latest.get("OpportunityScore"),
            first.get("OpportunityScore"),
        )

        search_volume_change = self._percentage_change(
            first.get("SearchVolume"),
            latest.get("SearchVolume"),
        )

        competition_change = self._difference(
            latest.get("CompetitionScore"),
            first.get("CompetitionScore"),
        )

        trend_change = self._difference(
            latest.get("GoogleTrendScore"),
            first.get("GoogleTrendScore"),
        )

        epc_change = self._percentage_change(
            first.get("EPC"),
            latest.get("EPC"),
        )

        refund_change = self._difference(
            latest.get("RefundRate"),
            first.get("RefundRate"),
        )

        cpc_change = self._difference(
            latest.get("EstimatedCPC"),
            first.get("EstimatedCPC"),
        )

        changes: list[str] = []

        changes.append(
            self._format_point_change(
                label="Opportunity score",
                value=score_change,
                positive_is_good=True,
            )
        )

        changes.append(
            self._format_percentage_change(
                label="Search volume",
                value=search_volume_change,
                positive_is_good=True,
            )
        )

        changes.append(
            self._format_point_change(
                label="Google Trends",
                value=trend_change,
                positive_is_good=True,
            )
        )

        changes.append(
            self._format_point_change(
                label="Competition",
                value=competition_change,
                positive_is_good=False,
            )
        )

        changes.append(
            self._format_percentage_change(
                label="EPC",
                value=epc_change,
                positive_is_good=True,
            )
        )

        changes.append(
            self._format_point_change(
                label="Refund rate",
                value=refund_change,
                positive_is_good=False,
                suffix=" percentage points",
            )
        )

        changes.append(
            self._format_point_change(
                label="Estimated CPC",
                value=cpc_change,
                positive_is_good=False,
                suffix="",
            )
        )

        improving_signals = self._count_positive_signals(
            score_change=score_change,
            search_volume_change=search_volume_change,
            competition_change=competition_change,
            trend_change=trend_change,
            epc_change=epc_change,
            refund_change=refund_change,
            cpc_change=cpc_change,
        )

        headline, summary, recommendation = (
            self._build_conclusion(
                score_change=score_change,
                improving_signals=improving_signals,
            )
        )

        return {
            "status": str(
                timeline.get("trend") or "Unknown"
            ),
            "headline": headline,
            "summary": summary,
            "changes": changes,
            "recommendation": recommendation,
            "improving_signals": improving_signals,
            "score_change": round(score_change, 2),
        }

    @staticmethod
    def _number(value: Any) -> float:
        if value is None:
            return 0.0

        return float(value)

    def _difference(
        self,
        latest: Any,
        first: Any,
    ) -> float:
        return self._number(latest) - self._number(first)

    def _percentage_change(
        self,
        first: Any,
        latest: Any,
    ) -> float:
        first_value = self._number(first)
        latest_value = self._number(latest)

        if first_value == 0:
            return 0.0

        return (
            (latest_value - first_value)
            / abs(first_value)
            * 100
        )

    @staticmethod
    def _format_point_change(
        *,
        label: str,
        value: float,
        positive_is_good: bool,
        suffix: str = " points",
    ) -> str:
        if value == 0:
            return f"{label} remained stable."

        improved = (
            value > 0
            if positive_is_good
            else value < 0
        )

        direction = "increased" if value > 0 else "decreased"
        indicator = "Positive" if improved else "Negative"

        return (
            f"{indicator}: {label} {direction} by "
            f"{abs(value):.2f}{suffix}."
        )

    @staticmethod
    def _format_percentage_change(
        *,
        label: str,
        value: float,
        positive_is_good: bool,
    ) -> str:
        if value == 0:
            return f"{label} remained stable."

        improved = (
            value > 0
            if positive_is_good
            else value < 0
        )

        direction = "increased" if value > 0 else "decreased"
        indicator = "Positive" if improved else "Negative"

        return (
            f"{indicator}: {label} {direction} by "
            f"{abs(value):.1f}%."
        )

    @staticmethod
    def _count_positive_signals(
        *,
        score_change: float,
        search_volume_change: float,
        competition_change: float,
        trend_change: float,
        epc_change: float,
        refund_change: float,
        cpc_change: float,
    ) -> int:
        signals = [
            score_change > 0,
            search_volume_change > 0,
            competition_change < 0,
            trend_change > 0,
            epc_change > 0,
            refund_change < 0,
            cpc_change < 0,
        ]

        return sum(signals)

    @staticmethod
    def _build_conclusion(
        *,
        score_change: float,
        improving_signals: int,
    ) -> tuple[str, str, str]:
        if score_change >= 10 and improving_signals >= 5:
            return (
                "Strong upward momentum",
                (
                    "The product is improving across several important "
                    "commercial and market indicators."
                ),
                (
                    "Continue the current strategy and consider increasing "
                    "the test budget gradually after validating conversions."
                ),
            )

        if score_change > 0 and improving_signals >= 4:
            return (
                "Positive momentum",
                (
                    "The opportunity is improving, supported by multiple "
                    "positive market signals."
                ),
                (
                    "Continue controlled testing and collect another snapshot "
                    "before scaling activity."
                ),
            )

        if score_change < 0 and improving_signals <= 2:
            return (
                "Opportunity is weakening",
                (
                    "The product is losing momentum across several important "
                    "indicators."
                ),
                (
                    "Pause expansion, review the offer and investigate whether "
                    "competition or demand has changed."
                ),
            )

        return (
            "Mixed market signals",
            (
                "Some indicators improved while others remained stable "
                "or moved in an unfavourable direction."
            ),
            (
                "Maintain a cautious test and collect more history before "
                "making a major investment decision."
            ),
        )