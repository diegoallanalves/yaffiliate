from __future__ import annotations

from app.models.comparison_result import (
    ComparisonResult,
    ComparisonWinner,
    ProductComparison,
)
from app.models.discovery_product import DiscoveryProduct


class ComparisonService:
    """
    Compares discovered products and produces business-focused
    rankings, badges, strengths, weaknesses and category winners.
    """

    def compare(
        self,
        products: list[DiscoveryProduct],
    ) -> ComparisonResult:
        if not products:
            return ComparisonResult(
                products=[],
                best_product=None,
                winners=[],
                recommendation=(
                    "No products are available for comparison."
                ),
                confidence_score=0.0,
            )

        ranked_products = sorted(
            products,
            key=lambda product: product.opportunity_score,
            reverse=True,
        )

        comparisons: list[ProductComparison] = []

        for rank, product in enumerate(
            ranked_products,
            start=1,
        ):
            comparisons.append(
                ProductComparison(
                    product=product,
                    rank=rank,
                    decision=self._get_decision(
                        product.opportunity_score
                    ),
                    badge=self._get_badge(
                        rank=rank,
                        product=product,
                    ),
                    seo_rating=self._calculate_seo_rating(
                        product
                    ),
                    confidence_score=self._calculate_confidence(
                        product
                    ),
                    strengths=self._get_strengths(
                        product
                    ),
                    weaknesses=self._get_weaknesses(
                        product
                    ),
                )
            )

        best_product = comparisons[0]

        winners = self._build_winners(
            ranked_products
        )

        confidence_score = round(
            sum(
                comparison.confidence_score
                for comparison in comparisons
            )
            / len(comparisons),
            1,
        )

        recommendation = (
            f"If you can test only one product, start with "
            f"{best_product.product.product_name}. It has the "
            f"highest opportunity score at "
            f"{best_product.product.opportunity_score:.1f}/100 "
            f"and currently ranks first overall."
        )

        return ComparisonResult(
            products=comparisons,
            best_product=best_product,
            winners=winners,
            recommendation=recommendation,
            confidence_score=confidence_score,
        )

    @staticmethod
    def _get_decision(
        opportunity_score: float,
    ) -> str:
        if opportunity_score >= 80:
            return "Prioritise"

        if opportunity_score >= 65:
            return "Best test candidate"

        if opportunity_score >= 55:
            return "Worth testing"

        if opportunity_score >= 45:
            return "Review carefully"

        return "Avoid for now"

    @staticmethod
    def _get_badge(
        *,
        rank: int,
        product: DiscoveryProduct,
    ) -> str:
        if rank == 1:
            return "🏆 Best Overall"

        if product.competition_score <= 40:
            return "🟢 Lowest Competition"

        if product.commission_amount >= 200:
            return "💰 Highest Commission"

        if product.google_trend_score >= 75:
            return "📈 Strong Trend"

        return "⭐ Worth Reviewing"

    @staticmethod
    def _calculate_seo_rating(
        product: DiscoveryProduct,
    ) -> int:
        rating = 1

        if product.search_volume >= 2000:
            rating += 1

        if product.search_volume >= 5000:
            rating += 1

        if product.competition_score <= 55:
            rating += 1

        if product.google_trend_score >= 70:
            rating += 1

        return min(rating, 5)

    @staticmethod
    def _calculate_confidence(
        product: DiscoveryProduct,
    ) -> float:
        signals = [
            product.opportunity_score > 0,
            product.commission_amount > 0,
            product.search_volume > 0,
            product.competition_score > 0,
            product.google_trend_score > 0,
            product.epc > 0,
            product.refund_rate >= 0,
        ]

        completeness = (
            sum(signals)
            / len(signals)
            * 100
        )

        score_quality = min(
            max(
                product.opportunity_score,
                0,
            ),
            100,
        )

        confidence = (
            completeness * 0.55
            + score_quality * 0.45
        )

        return round(confidence, 1)

    @staticmethod
    def _get_strengths(
        product: DiscoveryProduct,
    ) -> list[str]:
        strengths: list[str] = []

        if product.opportunity_score >= 65:
            strengths.append(
                "Opportunity score is above average."
            )

        if product.commission_amount >= 150:
            strengths.append(
                "Commission per sale is commercially attractive."
            )

        if product.search_volume >= 5000:
            strengths.append(
                "Search demand is strong."
            )

        if product.competition_score <= 45:
            strengths.append(
                "Competition is relatively manageable."
            )

        if product.google_trend_score >= 75:
            strengths.append(
                "Current trend interest is strong."
            )

        if product.epc >= 2.5:
            strengths.append(
                "EPC indicates good earning potential."
            )

        if product.refund_rate <= 5:
            strengths.append(
                "Refund rate is low."
            )

        if not strengths:
            strengths.append(
                "The product has enough data for further review."
            )

        return strengths

    @staticmethod
    def _get_weaknesses(
        product: DiscoveryProduct,
    ) -> list[str]:
        weaknesses: list[str] = []

        if product.opportunity_score < 55:
            weaknesses.append(
                "Opportunity score is currently weak."
            )

        if product.commission_amount < 100:
            weaknesses.append(
                "Commission may limit paid acquisition."
            )

        if product.search_volume < 2000:
            weaknesses.append(
                "Search demand is limited."
            )

        if product.competition_score >= 60:
            weaknesses.append(
                "Competition is high."
            )

        if product.estimated_cpc >= 3:
            weaknesses.append(
                "Estimated CPC may make paid traffic expensive."
            )

        if product.refund_rate >= 8:
            weaknesses.append(
                "Refund rate creates additional commercial risk."
            )

        if not weaknesses:
            weaknesses.append(
                "No major weakness was detected from the current data."
            )

        return weaknesses

    @staticmethod
    def _build_winners(
        products: list[DiscoveryProduct],
    ) -> list[ComparisonWinner]:
        if not products:
            return []

        best_overall = max(
            products,
            key=lambda product: product.opportunity_score,
        )

        highest_commission = max(
            products,
            key=lambda product: product.commission_amount,
        )

        lowest_competition = min(
            products,
            key=lambda product: product.competition_score,
        )

        strongest_trend = max(
            products,
            key=lambda product: product.google_trend_score,
        )

        highest_demand = max(
            products,
            key=lambda product: product.search_volume,
        )

        return [
            ComparisonWinner(
                category="Best Overall",
                product_name=best_overall.product_name,
                value=(
                    f"{best_overall.opportunity_score:.1f}/100"
                ),
                reason=(
                    "Highest opportunity score in the comparison."
                ),
            ),
            ComparisonWinner(
                category="Highest Commission",
                product_name=highest_commission.product_name,
                value=(
                    f"R$ "
                    f"{highest_commission.commission_amount:,.2f}"
                ),
                reason=(
                    "Offers the largest commission per sale."
                ),
            ),
            ComparisonWinner(
                category="Lowest Competition",
                product_name=lowest_competition.product_name,
                value=(
                    f"{lowest_competition.competition_score:.0f}/100"
                ),
                reason=(
                    "May be easier to enter than the other products."
                ),
            ),
            ComparisonWinner(
                category="Strongest Trend",
                product_name=strongest_trend.product_name,
                value=(
                    f"{strongest_trend.google_trend_score:.0f}/100"
                ),
                reason=(
                    "Shows the strongest current market interest."
                ),
            ),
            ComparisonWinner(
                category="Highest Demand",
                product_name=highest_demand.product_name,
                value=(
                    f"{highest_demand.search_volume:,} searches"
                ),
                reason=(
                    "Has the largest recorded monthly search volume."
                ),
            ),
        ]