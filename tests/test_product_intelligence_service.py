from pprint import pprint

from app.services.product_intelligence_service import (
    ProductIntelligenceService,
)


def main() -> None:
    service = ProductIntelligenceService()

    intelligence = service.get_product_intelligence(
        product_id=5
    )

    pprint(intelligence)


if __name__ == "__main__":
    main()