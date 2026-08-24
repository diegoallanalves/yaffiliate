"""Supabase repository for product opportunity history."""

from __future__ import annotations

from typing import Any

from app.services.supabase_service import SupabaseService


class OpportunityHistoryRepository:
    """Read and write authenticated user's product-history snapshots."""

    @staticmethod
    def _client():
        return SupabaseService().client

    def create_snapshot(
        self,
        *,
        product_id: int,
        opportunity_score: float,
        epc: float | None = None,
        gravity_score: float | None = None,
        search_volume: int | None = None,
        competition_score: float | None = None,
        estimated_cpc: float | None = None,
        google_trend_score: float | None = None,
        refund_rate: float | None = None,
    ) -> int:
        response = (
            self._client()
            .table("product_opportunity_history")
            .insert(
                {
                    "product_id": product_id,
                    "opportunity_score": opportunity_score,
                    "epc": epc,
                    "gravity_score": gravity_score,
                    "search_volume": search_volume,
                    "competition_score": competition_score,
                    "estimated_cpc": estimated_cpc,
                    "google_trend_score": google_trend_score,
                    "refund_rate": refund_rate,
                }
            )
            .execute()
        )

        rows = list(response.data or [])

        if not rows:
            raise RuntimeError(
                "Supabase did not return the created history snapshot."
            )

        return int(rows[0]["opportunity_history_id"])

    def list_for_product(
        self,
        product_id: int,
    ) -> list[dict[str, Any]]:
        response = (
            self._client()
            .table("product_opportunity_history")
            .select("*")
            .eq("product_id", product_id)
            .order("recorded_at")
            .order("opportunity_history_id")
            .execute()
        )

        return [
            self._format_row(row)
            for row in (response.data or [])
        ]

    def get_latest_for_product(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        response = (
            self._client()
            .table("product_opportunity_history")
            .select("*")
            .eq("product_id", product_id)
            .order("recorded_at", desc=True)
            .order("opportunity_history_id", desc=True)
            .limit(1)
            .execute()
        )

        rows = list(response.data or [])

        return self._format_row(rows[0]) if rows else None

    @staticmethod
    def _format_row(
        row: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "OpportunityHistoryID": row.get(
                "opportunity_history_id"
            ),
            "ProductID": row.get("product_id"),
            "OpportunityScore": row.get(
                "opportunity_score"
            ),
            "EPC": row.get("epc"),
            "GravityScore": row.get("gravity_score"),
            "SearchVolume": row.get("search_volume"),
            "CompetitionScore": row.get(
                "competition_score"
            ),
            "EstimatedCPC": row.get("estimated_cpc"),
            "GoogleTrendScore": row.get(
                "google_trend_score"
            ),
            "RefundRate": row.get("refund_rate"),
            "RecordedAt": row.get("recorded_at"),
        }
