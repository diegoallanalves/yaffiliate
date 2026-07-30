from __future__ import annotations

from typing import Any

from app.repositories.product_repository import ProductRepository


class PortfolioService:
    """
    Provides portfolio-level intelligence across all saved products.
    """

    def __init__(
        self,
        product_repository: ProductRepository | None = None,
    ) -> None:
        self.product_repository = (
            product_repository or ProductRepository()
        )

    def get_portfolio_summary(self) -> dict[str, Any]:
        products = self.product_repository.list_products()

        if not products:
            return {
                "products": [],
                "total_products": 0,
                "average_score": 0.0,
                "high_opportunity": 0,
                "needs_attention": 0,
                "avoid_count": 0,
                "top_product": None,
            }

        prepared_products: list[dict[str, Any]] = []

        for product in products:
            item = dict(product)

            opportunity_score = float(
                item.get("OpportunityScore") or 0
            )

            commission_amount = float(
                item.get("CommissionAmount") or 0
            )

            search_volume = int(
                item.get("SearchVolume") or 0
            )

            competition_score = float(
                item.get("CompetitionScore") or 0
            )

            google_trend_score = float(
                item.get("GoogleTrendScore") or 0
            )

            item["OpportunityScore"] = opportunity_score
            item["CommissionAmount"] = commission_amount
            item["SearchVolume"] = search_volume
            item["CompetitionScore"] = competition_score
            item["GoogleTrendScore"] = google_trend_score

            item["Decision"] = self._get_decision(
                opportunity_score
            )

            item["PriorityAction"] = self._get_priority_action(
                opportunity_score=opportunity_score,
                search_volume=search_volume,
                competition_score=competition_score,
                google_trend_score=google_trend_score,
            )

            prepared_products.append(item)

        prepared_products.sort(
            key=lambda product: product["OpportunityScore"],
            reverse=True,
        )

        for index, product in enumerate(
            prepared_products,
            start=1,
        ):
            product["Rank"] = index

        total_products = len(prepared_products)

        average_score = sum(
            product["OpportunityScore"]
            for product in prepared_products
        ) / total_products

        high_opportunity = sum(
            1
            for product in prepared_products
            if product["OpportunityScore"] >= 70
        )

        needs_attention = sum(
            1
            for product in prepared_products
            if 50 <= product["OpportunityScore"] < 70
        )

        avoid_count = sum(
            1
            for product in prepared_products
            if product["OpportunityScore"] < 50
        )

        top_product = (
            prepared_products[0]
            if prepared_products
            else None
        )

        return {
            "products": prepared_products,
            "total_products": total_products,
            "average_score": round(average_score, 2),
            "high_opportunity": high_opportunity,
            "needs_attention": needs_attention,
            "avoid_count": avoid_count,
            "top_product": top_product,
        }

    @staticmethod
    def _get_decision(
        opportunity_score: float,
    ) -> str:
        if opportunity_score >= 80:
            return "Prioritise"

        if opportunity_score >= 65:
            return "Test"

        if opportunity_score >= 50:
            return "Test cautiously"

        return "Avoid for now"

    @staticmethod
    def _get_priority_action(
        *,
        opportunity_score: float,
        search_volume: int,
        competition_score: float,
        google_trend_score: float,
    ) -> str:
        if opportunity_score < 50:
            return "Improve product data before investing"

        if (
            search_volume >= 3000
            and competition_score <= 55
        ):
            return "Build an SEO keyword cluster"

        if google_trend_score >= 70:
            return "Create trend-based content"

        if competition_score >= 70:
            return "Validate a narrower niche angle"

        return "Run a small controlled market test"