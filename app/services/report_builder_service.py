from __future__ import annotations

from app.models.business_consultant_report import (
    BusinessConsultantReport,
)
from app.models.discovery_product import DiscoveryProduct
from app.models.product_analysis import ProductAnalysis
from app.models.report_data import ReportData


class ReportBuilderService:
    """
    Builds a complete executive report from
    Filtrify analysis objects.
    """

    def build(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        consultant: BusinessConsultantReport,
        generated_for: str = "Filtrify Client",
    ) -> ReportData:
        """
        Assemble all structured intelligence into one
        renderer-independent report object.
        """
        return ReportData(
            title="Filtrify Affiliate Opportunity Report",
            subtitle=(
                f"Executive analysis for "
                f"{product.product_name}"
            ),
            generated_for=generated_for,
            executive_summary=(
                consultant.executive_summary
            ),
            best_product=product.product_name,
            business_consultant_summary=(
                analysis.headline
            ),
            commercial_strategy=(
                consultant.commercial_strategy
            ),
            seo_strategy=(
                consultant.seo_strategy
            ),
            google_ads_strategy=(
                consultant.google_ads_strategy
            ),
            email_strategy=(
                consultant.email_strategy
            ),
            landing_page_strategy=(
                consultant.landing_page_strategy
            ),
            risk_analysis=(
                consultant.risk_analysis
            ),
            final_verdict=(
                consultant.final_verdict
            ),
            strengths=list(
                analysis.strengths
            ),
            weaknesses=list(
                analysis.weaknesses
            ),
            recommendations=list(
                analysis.recommendations
            ),
            next_actions=list(
                consultant.next_actions
            ),
            confidence_score=float(
                consultant.confidence_score
            ),
        )