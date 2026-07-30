from app.services.opportunity_score_service import OpportunityFactors
from app.services.recommendation_service import RecommendationService


def main() -> None:
    service = RecommendationService()

    factors = OpportunityFactors(
        commission_amount=150,
        commission_percent=50,
        search_volume=5000,
        competition_score=45,
        estimated_cpc=1.80,
        google_trend_score=70,
        refund_rate=5,
        gravity_score=25,
        epc=2.50,
    )

    recommendation = service.generate(
        opportunity_score=61.5,
        factors=factors,
    )

    print(recommendation)


if __name__ == "__main__":
    main()