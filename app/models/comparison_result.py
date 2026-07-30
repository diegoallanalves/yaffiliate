from __future__ import annotations

from dataclasses import dataclass, field

from app.models.discovery_product import DiscoveryProduct


@dataclass(slots=True)
class ProductComparison:
    """
    Comparison information calculated for one discovered product.
    """

    product: DiscoveryProduct
    rank: int
    decision: str
    badge: str
    seo_rating: int
    confidence_score: float
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "Rank": self.rank,
            "ProductName": self.product.product_name,
            "NetworkName": self.product.network_name,
            "OpportunityScore": self.product.opportunity_score,
            "CommissionAmount": self.product.commission_amount,
            "SearchVolume": self.product.search_volume,
            "CompetitionScore": self.product.competition_score,
            "GoogleTrendScore": self.product.google_trend_score,
            "EPC": self.product.epc,
            "Decision": self.decision,
            "Badge": self.badge,
            "SEORating": self.seo_rating,
            "ConfidenceScore": self.confidence_score,
            "Strengths": self.strengths,
            "Weaknesses": self.weaknesses,
        }


@dataclass(slots=True)
class ComparisonWinner:
    """
    Represents one category winner in the comparison workspace.
    """

    category: str
    product_name: str
    value: str
    reason: str


@dataclass(slots=True)
class ComparisonResult:
    """
    Complete output returned by the future ComparisonService.
    """

    products: list[ProductComparison]
    best_product: ProductComparison | None
    winners: list[ComparisonWinner]
    recommendation: str
    confidence_score: float

    def to_dict(self) -> dict[str, object]:
        return {
            "Products": [
                product.to_dict()
                for product in self.products
            ],
            "BestProduct": (
                self.best_product.to_dict()
                if self.best_product is not None
                else None
            ),
            "Winners": [
                {
                    "Category": winner.category,
                    "ProductName": winner.product_name,
                    "Value": winner.value,
                    "Reason": winner.reason,
                }
                for winner in self.winners
            ],
            "Recommendation": self.recommendation,
            "ConfidenceScore": self.confidence_score,
        }