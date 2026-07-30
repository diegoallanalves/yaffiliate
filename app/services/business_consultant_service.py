from __future__ import annotations

from app.models.business_consultant_report import (
    BusinessConsultantReport,
)
from app.models.discovery_product import DiscoveryProduct
from app.models.product_analysis import ProductAnalysis


class BusinessConsultantService:
    """
    Produces an executive business report for one product.

    This sits above ProductAnalysisService and transforms
    technical analysis into business recommendations.
    """

    def generate(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> BusinessConsultantReport:

        return BusinessConsultantReport(

            executive_summary=self._executive_summary(
                product,
                analysis,
            ),

            commercial_strategy=self._commercial_strategy(
                analysis,
            ),

            seo_strategy=self._seo_strategy(
                product,
                analysis,
            ),

            google_ads_strategy=self._google_ads_strategy(
                product,
                analysis,
            ),

            email_strategy=self._email_strategy(
                analysis,
            ),

            landing_page_strategy=self._landing_page_strategy(
                analysis,
            ),

            risk_analysis=self._risk_analysis(
                product,
            ),

            next_actions=self._next_actions(
                analysis,
            ),

            final_verdict=self._final_verdict(
                analysis,
            ),

            confidence_score=analysis.confidence_score,
        )

    def _executive_summary(
        self,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> str:

        return (
            f"{product.product_name} shows "
            f"{analysis.commercial_potential.lower()} "
            "commercial potential. The combination of "
            f"{product.search_volume:,} monthly searches, "
            f"moderate competition ({product.competition_score:.0f}/100), "
            f"commission of R$ {product.commission_amount:,.2f}, "
            f"and EPC of {product.epc:.2f} suggests this "
            "product is worth testing under a controlled "
            "marketing strategy."
        )

    def _commercial_strategy(
        self,
        analysis: ProductAnalysis,
    ) -> str:

        if analysis.commercial_potential == "Excellent":
            return (
                "Scale aggressively after validating conversions."
            )

        if analysis.commercial_potential == "Strong":
            return (
                "Begin with controlled testing and increase "
                "investment after confirming results."
            )

        if analysis.commercial_potential == "Moderate":
            return (
                "Validate demand before committing significant "
                "marketing budget."
            )

        return (
            "Monitor this market but prioritise stronger opportunities."
        )

    def _seo_strategy(
        self,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> str:

        if analysis.seo_potential == "Excellent":
            return (
                f"Focus on long-form SEO content targeting "
                f'"{product.product_name}" and related '
                "informational keywords. Publish tutorials, "
                "comparisons and buying guides."
            )

        if analysis.seo_potential == "Strong":
            return (
                "SEO should be one of the primary acquisition "
                "channels."
            )

        return (
            "SEO can support the product but should not be the "
            "main growth channel."
        )

    def _google_ads_strategy(
        self,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> str:

        if analysis.google_ads_potential in (
            "Excellent",
            "Strong",
        ):
            return (
                f"Start with approximately "
                f"R$ {product.estimated_cpc * 10:,.2f}/day "
                "to validate conversion performance before "
                "scaling."
            )

        return (
            "Delay paid advertising until stronger commercial "
            "signals are available."
        )

    def _email_strategy(
        self,
        analysis: ProductAnalysis,
    ) -> str:

        return (
            "Build a four-email sequence: problem, education, "
            "case study and offer."
        )

    def _landing_page_strategy(
        self,
        analysis: ProductAnalysis,
    ) -> str:

        return (
            "Create a focused landing page with a strong hero "
            "section, benefits, testimonials, FAQ and a single "
            "call-to-action."
        )

    def _risk_analysis(
        self,
        product: DiscoveryProduct,
    ) -> str:

        if product.refund_rate <= 5:
            return (
                "Commercial risk appears relatively low. "
                "Continue monitoring refund rates and "
                "competition."
            )

        return (
            "Monitor refund rates carefully before scaling."
        )

    def _next_actions(
        self,
        analysis: ProductAnalysis,
    ) -> list[str]:

        return [
            "Research target keywords.",
            "Publish one SEO article.",
            "Build the landing page.",
            "Create the email funnel.",
            "Run a small paid advertising test.",
            "Review results after one week.",
        ]

    def _final_verdict(
        self,
        analysis: ProductAnalysis,
    ) -> str:

        if analysis.commercial_potential in (
            "Excellent",
            "Strong",
        ):
            return (
                "Excellent candidate for a content-first "
                "affiliate strategy."
            )

        if analysis.commercial_potential == "Moderate":
            return (
                "Worth testing, but validate performance "
                "carefully."
            )

        return (
            "Not recommended as a priority at this time."
        )