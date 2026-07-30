from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.repositories.sql_server import get_sql_server_engine


class OpportunityHistoryRepository:
    def __init__(self, engine: Engine | None = None) -> None:
        self.engine = engine or get_sql_server_engine()

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
        query = text(
            """
            INSERT INTO ProductOpportunityHistory (
                ProductID,
                OpportunityScore,
                EPC,
                GravityScore,
                SearchVolume,
                CompetitionScore,
                EstimatedCPC,
                GoogleTrendScore,
                RefundRate
            )
            OUTPUT INSERTED.OpportunityHistoryID
            VALUES (
                :product_id,
                :opportunity_score,
                :epc,
                :gravity_score,
                :search_volume,
                :competition_score,
                :estimated_cpc,
                :google_trend_score,
                :refund_rate
            )
            """
        )

        parameters = {
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

        with self.engine.begin() as connection:
            history_id = connection.execute(
                query,
                parameters,
            ).scalar_one()

        return int(history_id)

    def list_for_product(
        self,
        product_id: int,
    ) -> list[dict[str, Any]]:
        query = text(
            """
            SELECT
                OpportunityHistoryID,
                ProductID,
                OpportunityScore,
                EPC,
                GravityScore,
                SearchVolume,
                CompetitionScore,
                EstimatedCPC,
                GoogleTrendScore,
                RefundRate,
                RecordedAt
            FROM ProductOpportunityHistory
            WHERE ProductID = :product_id
            ORDER BY RecordedAt ASC, OpportunityHistoryID ASC
            """
        )

        with self.engine.connect() as connection:
            rows = connection.execute(
                query,
                {"product_id": product_id},
            ).mappings().all()

        return [dict(row) for row in rows]

    def get_latest_for_product(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        query = text(
            """
            SELECT TOP 1
                OpportunityHistoryID,
                ProductID,
                OpportunityScore,
                EPC,
                GravityScore,
                SearchVolume,
                CompetitionScore,
                EstimatedCPC,
                GoogleTrendScore,
                RefundRate,
                RecordedAt
            FROM ProductOpportunityHistory
            WHERE ProductID = :product_id
            ORDER BY RecordedAt DESC, OpportunityHistoryID DESC
            """
        )

        with self.engine.connect() as connection:
            row = connection.execute(
                query,
                {"product_id": product_id},
            ).mappings().first()

        return dict(row) if row else None