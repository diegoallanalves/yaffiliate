from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.models.recommendation import Recommendation
from app.repositories.sql_server import get_sql_server_engine


class RecommendationRepository:
    def __init__(self, engine: Engine | None = None) -> None:
        self.engine = engine or get_sql_server_engine()

    def create_recommendation(
        self,
        *,
        product_id: int,
        recommendation: Recommendation,
    ) -> int:
        query = text(
            """
            INSERT INTO ProductRecommendations (
                ProductID,
                OpportunityScore,
                OpportunityLevel,
                RiskLevel,
                Difficulty,
                RecommendedChannel,
                ExpectedROI,
                RecommendedBudget,
                Reasoning,
                NextActions
            )
            OUTPUT INSERTED.RecommendationID
            VALUES (
                :product_id,
                :opportunity_score,
                :opportunity_level,
                :risk_level,
                :difficulty,
                :recommended_channel,
                :expected_roi,
                :recommended_budget,
                :reasoning,
                :next_actions
            )
            """
        )

        parameters = {
            "product_id": product_id,
            "opportunity_score": recommendation.opportunity_score,
            "opportunity_level": recommendation.opportunity_level,
            "risk_level": recommendation.risk_level,
            "difficulty": recommendation.difficulty,
            "recommended_channel": recommendation.recommended_channel,
            "expected_roi": recommendation.expected_roi,
            "recommended_budget": recommendation.recommended_budget,
            "reasoning": json.dumps(
                recommendation.reasoning,
                ensure_ascii=False,
            ),
            "next_actions": json.dumps(
                recommendation.next_actions,
                ensure_ascii=False,
            ),
        }

        with self.engine.begin() as connection:
            recommendation_id = connection.execute(
                query,
                parameters,
            ).scalar_one()

        return int(recommendation_id)

    def get_latest_for_product(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        query = text(
            """
            SELECT TOP 1
                RecommendationID,
                ProductID,
                OpportunityScore,
                OpportunityLevel,
                RiskLevel,
                Difficulty,
                RecommendedChannel,
                ExpectedROI,
                RecommendedBudget,
                Reasoning,
                NextActions,
                CreatedAt
            FROM ProductRecommendations
            WHERE ProductID = :product_id
            ORDER BY CreatedAt DESC, RecommendationID DESC
            """
        )

        with self.engine.connect() as connection:
            row = connection.execute(
                query,
                {"product_id": product_id},
            ).mappings().first()

        if row is None:
            return None

        result = dict(row)

        result["Reasoning"] = json.loads(
            result["Reasoning"] or "[]"
        )

        result["NextActions"] = json.loads(
            result["NextActions"] or "[]"
        )

        return result

    def list_for_product(
        self,
        product_id: int,
    ) -> list[dict[str, Any]]:
        query = text(
            """
            SELECT
                RecommendationID,
                ProductID,
                OpportunityScore,
                OpportunityLevel,
                RiskLevel,
                Difficulty,
                RecommendedChannel,
                ExpectedROI,
                RecommendedBudget,
                Reasoning,
                NextActions,
                CreatedAt
            FROM ProductRecommendations
            WHERE ProductID = :product_id
            ORDER BY CreatedAt DESC, RecommendationID DESC
            """
        )

        with self.engine.connect() as connection:
            rows = connection.execute(
                query,
                {"product_id": product_id},
            ).mappings().all()

        recommendations: list[dict[str, Any]] = []

        for row in rows:
            item = dict(row)

            item["Reasoning"] = json.loads(
                item["Reasoning"] or "[]"
            )

            item["NextActions"] = json.loads(
                item["NextActions"] or "[]"
            )

            recommendations.append(item)

        return recommendations