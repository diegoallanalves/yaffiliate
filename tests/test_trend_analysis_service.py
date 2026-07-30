from pprint import pprint

from app.services.opportunity_timeline_service import (
    OpportunityTimelineService,
)
from app.services.trend_analysis_service import (
    TrendAnalysisService,
)


def main() -> None:
    timeline_service = OpportunityTimelineService()
    trend_service = TrendAnalysisService()

    timeline = timeline_service.get_product_timeline(
        product_id=5
    )

    analysis = trend_service.analyse(
        timeline
    )

    pprint(analysis)


if __name__ == "__main__":
    main()