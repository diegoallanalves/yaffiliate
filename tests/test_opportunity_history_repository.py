from pprint import pprint

from app.repositories.opportunity_history_repository import (
    OpportunityHistoryRepository,
)


def main() -> None:
    repository = OpportunityHistoryRepository()

    history_id = repository.create_snapshot(
        product_id=5,
        opportunity_score=68.20,
        epc=2.80,
        gravity_score=30,
        search_volume=6200,
        competition_score=40,
        estimated_cpc=1.70,
        google_trend_score=78,
        refund_rate=4,
    )

    print("Created history snapshot:", history_id)

    latest = repository.get_latest_for_product(
        product_id=5
    )

    print("Latest snapshot:")
    pprint(latest)

    history = repository.list_for_product(
        product_id=5
    )

    print("History count:", len(history))


if __name__ == "__main__":
    main()