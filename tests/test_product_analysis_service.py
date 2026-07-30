from pprint import pprint

from app.collectors.hotmart_collector import HotmartCollector
from app.services.comparison_service import ComparisonService
from app.services.product_analysis_service import (
    ProductAnalysisService,
)


def main() -> None:
    collector = HotmartCollector()
    comparison_service = ComparisonService()
    analysis_service = ProductAnalysisService()

    products = collector.search_products(
        keyword="Excel",
        country_code="BR",
        language_code="pt-BR",
        limit=10,
    )

    comparison_result = comparison_service.compare(
        products
    )

    if not products:
        print("No products were found.")
        return

    selected_product = products[0]

    selected_comparison = next(
        (
            item
            for item in comparison_result.products
            if item.product.product_name
            == selected_product.product_name
        ),
        None,
    )

    analysis = analysis_service.analyse(
        product=selected_product,
        comparison=selected_comparison,
    )

    pprint(analysis)


if __name__ == "__main__":
    main()