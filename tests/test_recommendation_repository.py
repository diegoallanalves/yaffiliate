from app.models.recommendation import Recommendation
from app.repositories.recommendation_repository import RecommendationRepository


def main() -> None:
    repository = RecommendationRepository()

    recommendation = Recommendation(
        opportunity_score=61.5,
        opportunity_level="Moderate",
        risk_level="Low",
        difficulty="Medium",
        recommended_channel="SEO",
        expected_roi="Medium",
        recommended_budget=108.0,
        reasoning=[
            "The overall opportunity score requires cautious testing.",
            "The commission per sale supports paid or content acquisition.",
        ],
        next_actions=[
            "Verify all product claims.",
            "Build a keyword cluster.",
        ],
    )

    recommendation_id = repository.create_recommendation(
        product_id=3,
        recommendation=recommendation,
    )

    print("Created recommendation:", recommendation_id)

    latest = repository.get_latest_for_product(3)

    print("Latest recommendation:")
    print(latest)

    history = repository.list_for_product(3)

    print("Recommendation history count:", len(history))


if __name__ == "__main__":
    main()