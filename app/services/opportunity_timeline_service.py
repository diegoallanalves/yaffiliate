from __future__ import annotations

from typing import Any

from app.repositories.opportunity_history_repository import (
    OpportunityHistoryRepository,
)


class OpportunityTimelineService:
    """
    Converts raw opportunity-history snapshots into timeline intelligence.
    """

    def __init__(
        self,
        history_repository: OpportunityHistoryRepository | None = None,
    ) -> None:
        self.history_repository = (
            history_repository or OpportunityHistoryRepository()
        )

    def get_product_timeline(
        self,
        product_id: int,
    ) -> dict[str, Any]:
        history = self.history_repository.list_for_product(
            product_id
        )

        if not history:
            return {
                "product_id": product_id,
                "history": [],
                "snapshot_count": 0,
                "current_score": 0.0,
                "first_score": 0.0,
                "highest_score": 0.0,
                "lowest_score": 0.0,
                "score_change": 0.0,
                "trend": "No data",
            }

        prepared_history: list[dict[str, Any]] = []

        for snapshot in history:
            item = dict(snapshot)

            item["OpportunityScore"] = float(
                item.get("OpportunityScore") or 0
            )

            item["EPC"] = float(
                item.get("EPC") or 0
            )

            item["GravityScore"] = float(
                item.get("GravityScore") or 0
            )

            item["SearchVolume"] = int(
                item.get("SearchVolume") or 0
            )

            item["CompetitionScore"] = float(
                item.get("CompetitionScore") or 0
            )

            item["EstimatedCPC"] = float(
                item.get("EstimatedCPC") or 0
            )

            item["GoogleTrendScore"] = float(
                item.get("GoogleTrendScore") or 0
            )

            item["RefundRate"] = float(
                item.get("RefundRate") or 0
            )

            prepared_history.append(item)

        scores = [
            snapshot["OpportunityScore"]
            for snapshot in prepared_history
        ]

        first_score = scores[0]
        current_score = scores[-1]
        score_change = current_score - first_score

        trend = self._get_trend(
            score_change=score_change,
            snapshot_count=len(prepared_history),
        )

        return {
            "product_id": product_id,
            "history": prepared_history,
            "snapshot_count": len(prepared_history),
            "current_score": round(current_score, 2),
            "first_score": round(first_score, 2),
            "highest_score": round(max(scores), 2),
            "lowest_score": round(min(scores), 2),
            "score_change": round(score_change, 2),
            "trend": trend,
        }

    @staticmethod
    def _get_trend(
        *,
        score_change: float,
        snapshot_count: int,
    ) -> str:
        if snapshot_count < 2:
            return "Insufficient history"

        if score_change >= 10:
            return "Improving strongly"

        if score_change >= 3:
            return "Improving"

        if score_change <= -10:
            return "Declining strongly"

        if score_change <= -3:
            return "Declining"

        return "Stable"
