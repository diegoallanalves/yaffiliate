from __future__ import annotations

from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.repositories.opportunity_history_repository import (
    OpportunityHistoryRepository,
)
from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import (
    RecommendationRepository,
)
from app.services.opportunity_score_service import (
    OpportunityFactors,
)
from app.services.recommendation_service import (
    RecommendationService,
)


class DiscoveryPortfolioService:
    """
    Saves a discovered product into the permanent Filtrify portfolio.

    The workflow:
    - checks whether the product already exists;
    - creates the product;
    - saves current product metrics;
    - creates an opportunity-history snapshot;
    - generates and saves a recommendation.
    """

    def __init__(
        self,
        product_repository: ProductRepository | None = None,
        recommendation_repository: RecommendationRepository | None = None,
        history_repository: OpportunityHistoryRepository | None = None,
        recommendation_service: RecommendationService | None = None,
    ) -> None:
        self.product_repository = (
            product_repository or ProductRepository()
        )

        self.recommendation_repository = (
            recommendation_repository or RecommendationRepository()
        )

        self.history_repository = (
            history_repository or OpportunityHistoryRepository()
        )

        self.recommendation_service = (
            recommendation_service or RecommendationService()
        )

    def save_to_portfolio(
        self,
        product: DiscoveryProduct,
    ) -> dict[str, Any]:
        existing_product = self._find_existing_product(
            product_name=product.product_name,
            network_name=product.network_name,
        )

        if existing_product is not None:
            return {
                "already_exists": True,
                "product_id": int(
                    existing_product["ProductID"]
                ),
                "product_name": str(
                    existing_product["ProductName"]
                ),
                "recommendation_id": None,
                "history_id": None,
                "opportunity_score": float(
                    existing_product.get(
                        "OpportunityScore"
                    )
                    or 0
                ),
            }

        network_id = self._resolve_network_id(
            product.network_name
        )

        product_id = self.product_repository.create_product(
            product_name=product.product_name,
            network_id=network_id,
            category=product.category,
            language_code=product.language_code,
            country_code=product.country_code,
            price=float(product.price),
            commission_amount=float(
                product.commission_amount
            ),
            commission_percent=float(
                product.commission_percent
            ),
            sales_page_url=product.sales_page_url,
            affiliate_url=product.affiliate_url,
            status="Research",
            notes=product.description,
        )

        self.product_repository.add_product_metric(
            product_id=product_id,
            epc=float(product.epc),
            gravity_score=float(
                product.gravity_score
            ),
            search_volume=int(
                product.search_volume
            ),
            competition_score=float(
                product.competition_score
            ),
            estimated_cpc=float(
                product.estimated_cpc
            ),
            google_trend_score=float(
                product.google_trend_score
            ),
            refund_rate=float(
                product.refund_rate
            ),
            opportunity_score=float(
                product.opportunity_score
            ),
            data_source=(
                f"Product Discovery - "
                f"{product.network_name}"
            ),
        )

        history_id = self.history_repository.create_snapshot(
            product_id=product_id,
            opportunity_score=float(
                product.opportunity_score
            ),
            epc=float(product.epc),
            gravity_score=float(
                product.gravity_score
            ),
            search_volume=int(
                product.search_volume
            ),
            competition_score=float(
                product.competition_score
            ),
            estimated_cpc=float(
                product.estimated_cpc
            ),
            google_trend_score=float(
                product.google_trend_score
            ),
            refund_rate=float(
                product.refund_rate
            ),
        )

        opportunity_factors = OpportunityFactors(
            commission_amount=float(
                product.commission_amount
            ),
            commission_percent=float(
                product.commission_percent
            ),
            search_volume=int(
                product.search_volume
            ),
            competition_score=float(
                product.competition_score
            ),
            estimated_cpc=float(
                product.estimated_cpc
            ),
            google_trend_score=float(
                product.google_trend_score
            ),
            refund_rate=float(
                product.refund_rate
            ),
            gravity_score=float(
                product.gravity_score
            ),
            epc=float(product.epc),
        )

        recommendation = self.recommendation_service.generate(
            opportunity_score=float(
                product.opportunity_score
            ),
            factors=opportunity_factors,
        )

        recommendation_id = (
            self.recommendation_repository.create_recommendation(
                product_id=product_id,
                recommendation=recommendation,
            )
        )

        return {
            "already_exists": False,
            "product_id": product_id,
            "recommendation_id": recommendation_id,
            "history_id": history_id,
            "opportunity_score": float(
                product.opportunity_score
            ),
            "product_name": product.product_name,
        }

    def _find_existing_product(
        self,
        *,
        product_name: str,
        network_name: str,
    ) -> dict[str, Any] | None:
        products = self.product_repository.list_products(
            search=product_name,
        )

        cleaned_product_name = (
            product_name.strip().casefold()
        )

        cleaned_network_name = (
            network_name.strip().casefold()
        )

        for saved_product in products:
            saved_name = str(
                saved_product.get("ProductName") or ""
            ).strip().casefold()

            saved_network = str(
                saved_product.get("NetworkName") or ""
            ).strip().casefold()

            if (
                saved_name == cleaned_product_name
                and saved_network == cleaned_network_name
            ):
                return saved_product

        return None

    def _resolve_network_id(
        self,
        network_name: str,
    ) -> int | None:
        networks = (
            self.product_repository.list_affiliate_networks()
        )

        cleaned_name = (
            network_name.strip().casefold()
        )

        for network in networks:
            saved_name = str(
                network.get("NetworkName") or ""
            ).strip().casefold()

            if saved_name == cleaned_name:
                return int(network["NetworkID"])

        return None