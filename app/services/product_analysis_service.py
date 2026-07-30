from __future__ import annotations

from app.models.comparison_result import ProductComparison
from app.models.discovery_product import DiscoveryProduct
from app.models.product_analysis import ProductAnalysis


class ProductAnalysisService:
    """
    Converts product and comparison data into a business-focused analysis.
    """

    def analyse(
        self,
        product: DiscoveryProduct,
        comparison: ProductComparison | None = None,
    ) -> ProductAnalysis:
        strengths = self._get_strengths(
            product=product,
            comparison=comparison,
        )

        weaknesses = self._get_weaknesses(
            product=product,
            comparison=comparison,
        )

        commercial_potential = self._commercial_potential(
            product
        )

        seo_potential = self._seo_potential(
            product
        )

        google_ads_potential = self._google_ads_potential(
            product
        )

        email_marketing_potential = (
            self._email_marketing_potential(
                product
            )
        )

        landing_page_potential = (
            self._landing_page_potential(
                product
            )
        )

        target_audience = self._target_audience(
            product
        )

        recommendations = self._recommendations(
            product=product,
            seo_potential=seo_potential,
            google_ads_potential=google_ads_potential,
            email_marketing_potential=(
                email_marketing_potential
            ),
            landing_page_potential=(
                landing_page_potential
            ),
        )

        probability_of_success = (
            self._probability_of_success(
                product=product,
                comparison=comparison,
            )
        )

        confidence_score = (
            comparison.confidence_score
            if comparison is not None
            else self._confidence_score(product)
        )

        headline = self._headline(
            product=product,
            commercial_potential=commercial_potential,
            seo_potential=seo_potential,
        )

        return ProductAnalysis(
            headline=headline,
            commercial_potential=commercial_potential,
            seo_potential=seo_potential,
            google_ads_potential=google_ads_potential,
            email_marketing_potential=(
                email_marketing_potential
            ),
            landing_page_potential=(
                landing_page_potential
            ),
            target_audience=target_audience,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            probability_of_success=probability_of_success,
            confidence_score=confidence_score,
        )

    @staticmethod
    def _commercial_potential(
        product: DiscoveryProduct,
    ) -> str:
        score = product.opportunity_score

        if (
            score >= 75
            and product.commission_amount >= 150
            and product.refund_rate <= 5
        ):
            return "Excellent"

        if (
            score >= 65
            and product.commission_amount >= 100
        ):
            return "Strong"

        if score >= 55:
            return "Moderate"

        return "Limited"

    @staticmethod
    def _seo_potential(
        product: DiscoveryProduct,
    ) -> str:
        if (
            product.search_volume >= 5000
            and product.competition_score <= 45
            and product.google_trend_score >= 70
        ):
            return "Excellent"

        if (
            product.search_volume >= 3000
            and product.competition_score <= 60
        ):
            return "Strong"

        if product.search_volume >= 1500:
            return "Moderate"

        return "Limited"

    @staticmethod
    def _google_ads_potential(
        product: DiscoveryProduct,
    ) -> str:
        commission_to_cpc = (
            product.commission_amount
            / max(product.estimated_cpc, 0.01)
        )

        if (
            commission_to_cpc >= 70
            and product.epc >= 2.5
            and product.refund_rate <= 5
        ):
            return "Excellent"

        if (
            commission_to_cpc >= 40
            and product.epc >= 1.8
        ):
            return "Strong"

        if commission_to_cpc >= 20:
            return "Moderate"

        return "Limited"

    @staticmethod
    def _email_marketing_potential(
        product: DiscoveryProduct,
    ) -> str:
        if (
            product.commission_amount >= 150
            and product.refund_rate <= 5
        ):
            return "Excellent"

        if (
            product.commission_amount >= 100
            and product.refund_rate <= 7
        ):
            return "Strong"

        if product.commission_amount >= 60:
            return "Moderate"

        return "Limited"

    @staticmethod
    def _landing_page_potential(
        product: DiscoveryProduct,
    ) -> str:
        if (
            product.opportunity_score >= 65
            and product.google_trend_score >= 70
        ):
            return "Excellent"

        if product.opportunity_score >= 55:
            return "Strong"

        if product.opportunity_score >= 45:
            return "Moderate"

        return "Limited"

    @staticmethod
    def _target_audience(
        product: DiscoveryProduct,
    ) -> list[str]:
        searchable_text = (
            f"{product.product_name} "
            f"{product.category or ''} "
            f"{product.description or ''}"
        ).casefold()

        audience: list[str] = []

        if "excel" in searchable_text:
            audience.extend(
                [
                    "Office workers",
                    "Students",
                    "Business analysts",
                    "Administrative professionals",
                ]
            )

        if "power bi" in searchable_text:
            audience.extend(
                [
                    "Data analysts",
                    "Business intelligence professionals",
                    "Managers",
                    "Reporting teams",
                ]
            )

        if "python" in searchable_text:
            audience.extend(
                [
                    "Aspiring data professionals",
                    "Developers",
                    "University students",
                    "Career changers",
                ]
            )

        if "marketing" in searchable_text:
            audience.extend(
                [
                    "Small-business owners",
                    "Freelancers",
                    "Content creators",
                    "Marketing professionals",
                ]
            )

        if not audience:
            audience.extend(
                [
                    "Beginners interested in the topic",
                    "Professionals seeking practical skills",
                    "People comparing training options",
                ]
            )

        return list(dict.fromkeys(audience))

    def _get_strengths(
        self,
        *,
        product: DiscoveryProduct,
        comparison: ProductComparison | None,
    ) -> list[str]:
        strengths: list[str] = []

        if product.opportunity_score >= 65:
            strengths.append(
                "The opportunity score is above average."
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
                "Competition appears manageable."
            )

        if product.google_trend_score >= 75:
            strengths.append(
                "Current market interest is strong."
            )

        if product.epc >= 2.5:
            strengths.append(
                "EPC indicates good earning potential."
            )

        if product.refund_rate <= 5:
            strengths.append(
                "Refund rate is low."
            )

        if (
            comparison is not None
            and comparison.rank == 1
        ):
            strengths.append(
                "This product ranks first in the current comparison."
            )

        if not strengths:
            strengths.append(
                "The product has enough data for controlled testing."
            )

        return strengths

    @staticmethod
    def _get_weaknesses(
        *,
        product: DiscoveryProduct,
        comparison: ProductComparison | None,
    ) -> list[str]:
        weaknesses: list[str] = []

        if product.competition_score >= 60:
            weaknesses.append(
                "Competition is high and may slow organic growth."
            )

        if product.search_volume < 2000:
            weaknesses.append(
                "Search demand is relatively limited."
            )

        if product.estimated_cpc >= 3:
            weaknesses.append(
                "Paid traffic may be expensive."
            )

        if product.refund_rate >= 8:
            weaknesses.append(
                "Refund levels create additional commercial risk."
            )

        if product.commission_amount < 100:
            weaknesses.append(
                "The commission may restrict paid acquisition."
            )

        if (
            comparison is not None
            and comparison.rank > 1
        ):
            weaknesses.append(
                (
                    f"The product ranks {comparison.rank} in the "
                    "current comparison."
                )
            )

        if not weaknesses:
            weaknesses.append(
                "No major weakness was detected from the current data."
            )

        return weaknesses

    @staticmethod
    def _recommendations(
        *,
        product: DiscoveryProduct,
        seo_potential: str,
        google_ads_potential: str,
        email_marketing_potential: str,
        landing_page_potential: str,
    ) -> list[str]:
        recommendations: list[str] = []

        if seo_potential in {"Excellent", "Strong"}:
            recommendations.append(
                "Build a keyword cluster and publish helpful SEO content."
            )

        if google_ads_potential in {"Excellent", "Strong"}:
            recommendations.append(
                "Run a small paid-search test before increasing budget."
            )

        if email_marketing_potential in {"Excellent", "Strong"}:
            recommendations.append(
                "Create a short email sequence with education before promotion."
            )

        if landing_page_potential in {"Excellent", "Strong"}:
            recommendations.append(
                "Build a focused landing page with one clear call to action."
            )

        if product.refund_rate > 5:
            recommendations.append(
                "Review customer feedback and refund causes before scaling."
            )

        recommendations.append(
            "Validate all product claims and affiliate-network rules."
        )

        recommendations.append(
            "Collect conversion data before making a large investment."
        )

        return recommendations

    @staticmethod
    def _probability_of_success(
        *,
        product: DiscoveryProduct,
        comparison: ProductComparison | None,
    ) -> float:
        value = (
            product.opportunity_score * 0.55
            + product.google_trend_score * 0.15
            + min(product.search_volume / 100, 100) * 0.10
            + max(100 - product.competition_score, 0) * 0.10
            + min(product.epc * 20, 100) * 0.10
        )

        if product.refund_rate > 5:
            value -= (
                product.refund_rate - 5
            ) * 1.5

        if (
            comparison is not None
            and comparison.rank == 1
        ):
            value += 4

        return round(
            min(
                max(value, 0),
                100,
            ),
            1,
        )

    @staticmethod
    def _confidence_score(
        product: DiscoveryProduct,
    ) -> float:
        populated_signals = [
            product.opportunity_score > 0,
            product.commission_amount > 0,
            product.search_volume > 0,
            product.competition_score > 0,
            product.google_trend_score > 0,
            product.epc > 0,
            product.estimated_cpc > 0,
            product.refund_rate >= 0,
        ]

        return round(
            sum(populated_signals)
            / len(populated_signals)
            * 100,
            1,
        )

    @staticmethod
    def _headline(
        *,
        product: DiscoveryProduct,
        commercial_potential: str,
        seo_potential: str,
    ) -> str:
        if (
            commercial_potential in {"Excellent", "Strong"}
            and seo_potential in {"Excellent", "Strong"}
        ):
            return (
                f"{product.product_name} is a strong candidate "
                "for controlled promotion."
            )

        if commercial_potential == "Moderate":
            return (
                f"{product.product_name} may be worth testing, "
                "but the evidence is mixed."
            )

        return (
            f"{product.product_name} should not be prioritised yet."
        )