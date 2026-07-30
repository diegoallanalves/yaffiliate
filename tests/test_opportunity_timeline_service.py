from pprint import pprint

from app.services.opportunity_timeline_service import (
    OpportunityTimelineService,
)


def main() -> None:
    service = OpportunityTimelineService()

    timeline = service.get_product_timeline(
        product_id=5
    )

    pprint(timeline)


if __name__ == "__main__":
    main()