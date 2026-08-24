"""Supabase repository for product recommendations."""

from __future__ import annotations

import json
from typing import Any

from app.models.recommendation import Recommendation
from app.services.supabase_service import SupabaseService


class RecommendationRepository:
    """Read and write authenticated user's product recommendations."""

    @staticmethod
    def _client():
        return SupabaseService().client

    def create_recommendation(
        self,
        *,
        product_id: int,
        recommendation: Recommendation,
    ) -> int:
        response = (
            self._client()
            .table("product_recommendations")
            .insert(
                {
                    "product_id": product_id,
                    "opportunity_score": recommendation.opportunity_score,
                    "opportunity_level": recommendation.opportunity_level,
                    "risk_level": recommendation.risk_level,
                    "difficulty": recommendation.difficulty,
                    "recommended_channel": recommendation.recommended_channel,
                    "expected_roi": recommendation.expected_roi,
                    "recommended_budget": recommendation.recommended_budget,
                    "reasoning": recommendation.reasoning,
                    "next_actions": recommendation.next_actions,
                }
            )
            .execute()
        )

        rows = list(response.data or [])

        if not rows:
            raise RuntimeError(
                "Supabase did not return the created recommendation."
            )

        return int(rows[0]["recommendation_id"])

    def get_latest_for_product(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        response = (
            self._client()
            .table("product_recommendations")
            .select("*")
            .eq("product_id", product_id)
            .order("created_at", desc=True)
            .order("recommendation_id", desc=True)
            .limit(1)
            .execute()
        )

        rows = list(response.data or [])

        return self._format_row(rows[0]) if rows else None

    def list_for_product(
        self,
        product_id: int,
    ) -> list[dict[str, Any]]:
        response = (
            self._client()
            .table("product_recommendations")
            .select("*")
            .eq("product_id", product_id)
            .order("created_at", desc=True)
            .order("recommendation_id", desc=True)
            .execute()
        )

        return [
            self._format_row(row)
            for row in (response.data or [])
        ]

    @staticmethod
    def _json_list(value: Any) -> list[Any]:
        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            try:
                decoded = json.loads(value)
                return (
                    decoded
                    if isinstance(decoded, list)
                    else []
                )
            except json.JSONDecodeError:
                return []

        return []

    @classmethod
    def _format_row(
        cls,
        row: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "RecommendationID": row.get(
                "recommendation_id"
            ),
            "ProductID": row.get("product_id"),
            "OpportunityScore": row.get(
                "opportunity_score"
            ),
            "OpportunityLevel": row.get(
                "opportunity_level"
            ),
            "RiskLevel": row.get("risk_level"),
            "Difficulty": row.get("difficulty"),
            "RecommendedChannel": row.get(
                "recommended_channel"
            ),
            "ExpectedROI": row.get("expected_roi"),
            "RecommendedBudget": row.get(
                "recommended_budget"
            ),
            "Reasoning": cls._json_list(
                row.get("reasoning")
            ),
            "NextActions": cls._json_list(
                row.get("next_actions")
            ),
            "CreatedAt": row.get("created_at"),
        }
