from pprint import pprint

from app.collectors.hotmart_collector import HotmartCollector
from app.services.comparison_service import ComparisonService
from app.services.landing_page_service import (
    LandingPageService,
)
from app.services.product_analysis_service import (
    ProductAnalysisService,
)


def main() -> None:
    """
    Test the Landing Page generator.

    CTA = Call to Action.

    A CTA is the text or button that encourages a visitor
    to take the next step, such as "View the Official Offer".
    """

    collector = HotmartCollector()
    comparison_service = ComparisonService()
    analysis_service = ProductAnalysisService()
    landing_page_service = LandingPageService()

    products = collector.search_products(
        keyword="Excel",
        country_code="BR",
        language_code="pt-BR",
        limit=10,
    )

    if not products:
        print("No products were found.")
        return

    comparison = comparison_service.compare(
        products
    )

    selected_product = products[0]

    selected_comparison = next(
        (
            item
            for item in comparison.products
            if (
                item.product.product_name
                == selected_product.product_name
            )
        ),
        None,
    )

    analysis = analysis_service.analyse(
        product=selected_product,
        comparison=selected_comparison,
    )

    landing_page = landing_page_service.generate(
        product=selected_product,
        analysis=analysis,
        target_audience=(
            "Office professionals and business analysts"
        ),
        primary_goal="Visit Sales Page",
        tone="Persuasive",
    )

    pprint(
        landing_page
    )


if __name__ == "__main__":
    main()