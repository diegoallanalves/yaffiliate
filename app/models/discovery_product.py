from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DiscoveryProduct:
    """
    Standard product format returned by all discovery collectors.
    """

    product_name: str
    network_name: str
    category: str | None
    country_code: str | None
    language_code: str | None

    price: float
    commission_amount: float
    commission_percent: float

    epc: float
    gravity_score: float
    search_volume: int
    competition_score: float
    estimated_cpc: float
    google_trend_score: float
    refund_rate: float

    opportunity_score: float

    sales_page_url: str | None
    affiliate_url: str | None
    description: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "ProductName": self.product_name,
            "NetworkName": self.network_name,
            "Category": self.category,
            "CountryCode": self.country_code,
            "LanguageCode": self.language_code,
            "Price": self.price,
            "CommissionAmount": self.commission_amount,
            "CommissionPercent": self.commission_percent,
            "EPC": self.epc,
            "GravityScore": self.gravity_score,
            "SearchVolume": self.search_volume,
            "CompetitionScore": self.competition_score,
            "EstimatedCPC": self.estimated_cpc,
            "GoogleTrendScore": self.google_trend_score,
            "RefundRate": self.refund_rate,
            "OpportunityScore": self.opportunity_score,
            "SalesPageURL": self.sales_page_url,
            "AffiliateURL": self.affiliate_url,
            "Description": self.description,
        }