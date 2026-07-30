from __future__ import annotations

from typing import Any

from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import (
    RecommendationRepository,
)


class ProductIntelligenceService:
    """
    Combines product data, latest metrics and latest recommendation
    into one intelligence record for the Streamlit interface.
    """

    def __init__(
        self,
        product_repository: ProductRepository | None = None,
        recommendation_repository: RecommendationRepository | None = None,
    ) -> None:
        self.product_repository = (
            product_repository or ProductRepository()
        )

        self.recommendation_repository = (
            recommendation_repository or RecommendationRepository()
        )

    def get_product_intelligence(
        self,
        product_id: int,
    ) -> dict[str, Any] | None:
        product = self.product_repository.get_product(
            product_id
        )

        if product is None:
            return None

        latest_metric = (
            self.product_repository.get_latest_product_metric(
                product_id
            )
        )

        latest_recommendation = (
            self.recommendation_repository.get_latest_for_product(
                product_id
            )
        )

        return {
            "product": product,
            "latest_metric": latest_metric,
            "latest_recommendation": latest_recommendation,
        }