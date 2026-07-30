from pprint import pprint

from app.collectors.hotmart_collector import HotmartCollector
from app.services.comparison_service import ComparisonService
from app.services.product_analysis_service import (
    ProductAnalysisService,
)
from app.services.seo_article_service import (
    SEOArticleService,
)


def main() -> None:
    collector = HotmartCollector()
    comparison_service = ComparisonService()
    analysis_service = ProductAnalysisService()
    article_service = SEOArticleService()

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

    article = article_service.generate(
        product=selected_product,
        analysis=analysis,
        target_keyword="Excel course",
    )

    pprint(article)


if __name__ == "__main__":
    main()