from __future__ import annotations

from app.collectors.base_collector import BaseCollector
from app.models.discovery_product import DiscoveryProduct
from app.services.opportunity_score_service import (
    OpportunityFactors,
    OpportunityScoreService,
)


class HotmartCollector(BaseCollector):
    """
    Mock Hotmart collector with realistic catalogue search behaviour.

    Products come from a fixed local catalogue. Search results are filtered
    by product name, category and description. Later, this catalogue can be
    replaced by an authorised Hotmart API or data source without changing
    ProductDiscoveryService or the UI.
    """

    network_name = "Hotmart"

    MOCK_CATALOGUE = [
        {
            "product_name": "Excel Masterclass",
            "category": "Education",
            "country_code": "BR",
            "language_code": "pt-BR",
            "price": 297.00,
            "commission_amount": 150.00,
            "commission_percent": 50.00,
            "epc": 2.80,
            "gravity_score": 34.00,
            "search_volume": 6200,
            "competition_score": 42.00,
            "estimated_cpc": 1.70,
            "google_trend_score": 78.00,
            "refund_rate": 4.00,
            "description": (
                "Complete Excel training covering formulas, dashboards, "
                "automation and practical spreadsheet projects."
            ),
            "sales_page_url": (
                "https://example.com/hotmart/excel-masterclass"
            ),
        },
        {
            "product_name": "Excel Fast Track",
            "category": "Education",
            "country_code": "BR",
            "language_code": "pt-BR",
            "price": 197.00,
            "commission_amount": 90.00,
            "commission_percent": 45.00,
            "epc": 1.90,
            "gravity_score": 22.00,
            "search_volume": 4100,
            "competition_score": 38.00,
            "estimated_cpc": 1.25,
            "google_trend_score": 69.00,
            "refund_rate": 6.00,
            "description": (
                "Beginner-friendly Excel course designed for fast, "
                "practical learning."
            ),
            "sales_page_url": (
                "https://example.com/hotmart/excel-fast-track"
            ),
        },
        {
            "product_name": "Advanced Excel Blueprint",
            "category": "Business",
            "country_code": "BR",
            "language_code": "pt-BR",
            "price": 497.00,
            "commission_amount": 225.00,
            "commission_percent": 45.00,
            "epc": 3.20,
            "gravity_score": 41.00,
            "search_volume": 2900,
            "competition_score": 61.00,
            "estimated_cpc": 2.90,
            "google_trend_score": 73.00,
            "refund_rate": 7.00,
            "description": (
                "Advanced Excel strategy programme for professionals, "
                "analysts and business users."
            ),
            "sales_page_url": (
                "https://example.com/hotmart/advanced-excel-blueprint"
            ),
        },
        {
            "product_name": "Power BI Dashboard Pro",
            "category": "Data Analytics",
            "country_code": "BR",
            "language_code": "pt-BR",
            "price": 347.00,
            "commission_amount": 170.00,
            "commission_percent": 49.00,
            "epc": 2.95,
            "gravity_score": 37.00,
            "search_volume": 5400,
            "competition_score": 47.00,
            "estimated_cpc": 2.10,
            "google_trend_score": 81.00,
            "refund_rate": 4.50,
            "description": (
                "Power BI course focused on dashboards, DAX, data modelling "
                "and business intelligence projects."
            ),
            "sales_page_url": (
                "https://example.com/hotmart/power-bi-dashboard-pro"
            ),
        },
        {
            "product_name": "Python for Data Science",
            "category": "Technology",
            "country_code": "BR",
            "language_code": "pt-BR",
            "price": 397.00,
            "commission_amount": 185.00,
            "commission_percent": 46.50,
            "epc": 2.65,
            "gravity_score": 31.00,
            "search_volume": 7200,
            "competition_score": 58.00,
            "estimated_cpc": 2.40,
            "google_trend_score": 84.00,
            "refund_rate": 5.00,
            "description": (
                "Practical Python course covering pandas, visualisation, "
                "machine learning and data-analysis projects."
            ),
            "sales_page_url": (
                "https://example.com/hotmart/python-for-data-science"
            ),
        },
        {
            "product_name": "Digital Marketing Accelerator",
            "category": "Marketing",
            "country_code": "BR",
            "language_code": "pt-BR",
            "price": 297.00,
            "commission_amount": 140.00,
            "commission_percent": 47.00,
            "epc": 2.30,
            "gravity_score": 29.00,
            "search_volume": 6800,
            "competition_score": 66.00,
            "estimated_cpc": 2.75,
            "google_trend_score": 76.00,
            "refund_rate": 6.50,
            "description": (
                "Digital marketing course covering content, paid traffic, "
                "funnels, email marketing and social media."
            ),
            "sales_page_url": (
                "https://example.com/hotmart/digital-marketing-accelerator"
            ),
        },
    ]

    def __init__(
        self,
        score_service: OpportunityScoreService | None = None,
    ) -> None:
        self.score_service = (
            score_service or OpportunityScoreService()
        )

    def search_products(
        self,
        *,
        keyword: str,
        country_code: str | None = None,
        language_code: str | None = None,
        limit: int = 20,
    ) -> list[DiscoveryProduct]:
        cleaned_keyword = keyword.strip().casefold()

        if not cleaned_keyword:
            return []

        matching_items = [
            item
            for item in self.MOCK_CATALOGUE
            if self._matches_keyword(
                item,
                cleaned_keyword,
            )
            and self._matches_country(
                item,
                country_code,
            )
            and self._matches_language(
                item,
                language_code,
            )
        ]

        products = [
            self._to_discovery_product(item)
            for item in matching_items
        ]

        products.sort(
            key=lambda product: product.opportunity_score,
            reverse=True,
        )

        return products[: max(limit, 0)]

    @staticmethod
    def _matches_keyword(
        item: dict[str, object],
        cleaned_keyword: str,
    ) -> bool:
        searchable_text = " ".join(
            [
                str(item.get("product_name") or ""),
                str(item.get("category") or ""),
                str(item.get("description") or ""),
            ]
        ).casefold()

        keyword_terms = [
            term
            for term in cleaned_keyword.split()
            if term
        ]

        return all(
            term in searchable_text
            for term in keyword_terms
        )

    @staticmethod
    def _matches_country(
        item: dict[str, object],
        country_code: str | None,
    ) -> bool:
        if not country_code:
            return True

        saved_country = str(
            item.get("country_code") or ""
        ).casefold()

        return saved_country == country_code.strip().casefold()

    @staticmethod
    def _matches_language(
        item: dict[str, object],
        language_code: str | None,
    ) -> bool:
        if not language_code:
            return True

        saved_language = str(
            item.get("language_code") or ""
        ).casefold()

        return saved_language == language_code.strip().casefold()

    def _to_discovery_product(
        self,
        item: dict[str, object],
    ) -> DiscoveryProduct:
        factors = OpportunityFactors(
            commission_amount=float(
                item["commission_amount"]
            ),
            commission_percent=float(
                item["commission_percent"]
            ),
            search_volume=int(
                item["search_volume"]
            ),
            competition_score=float(
                item["competition_score"]
            ),
            estimated_cpc=float(
                item["estimated_cpc"]
            ),
            google_trend_score=float(
                item["google_trend_score"]
            ),
            refund_rate=float(
                item["refund_rate"]
            ),
            gravity_score=float(
                item["gravity_score"]
            ),
            epc=float(
                item["epc"]
            ),
        )

        opportunity_score = self.score_service.calculate(
            factors
        )

        return DiscoveryProduct(
            product_name=str(
                item["product_name"]
            ),
            network_name=self.network_name,
            category=str(
                item["category"]
            ),
            country_code=str(
                item["country_code"]
            ),
            language_code=str(
                item["language_code"]
            ),
            price=float(
                item["price"]
            ),
            commission_amount=float(
                item["commission_amount"]
            ),
            commission_percent=float(
                item["commission_percent"]
            ),
            epc=float(
                item["epc"]
            ),
            gravity_score=float(
                item["gravity_score"]
            ),
            search_volume=int(
                item["search_volume"]
            ),
            competition_score=float(
                item["competition_score"]
            ),
            estimated_cpc=float(
                item["estimated_cpc"]
            ),
            google_trend_score=float(
                item["google_trend_score"]
            ),
            refund_rate=float(
                item["refund_rate"]
            ),
            opportunity_score=float(
                opportunity_score
            ),
            sales_page_url=str(
                item["sales_page_url"]
            ),
            affiliate_url=None,
            description=str(
                item["description"]
            ),
        )