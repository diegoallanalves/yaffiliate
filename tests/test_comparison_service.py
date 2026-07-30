from pprint import pprint

from app.collectors.hotmart_collector import HotmartCollector
from app.services.comparison_service import ComparisonService


def main() -> None:
    collector = HotmartCollector()
    comparison_service = ComparisonService()

    products = collector.search_products(
        keyword="Excel",
        country_code="BR",
        language_code="pt-BR",
        limit=10,
    )

    comparison = comparison_service.compare(
        products
    )

    pprint(comparison.to_dict())


if __name__ == "__main__":
    main()