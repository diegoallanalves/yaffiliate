from pprint import pprint

from app.collectors.hotmart_collector import HotmartCollector
from app.services.discovery_portfolio_service import (
    DiscoveryPortfolioService,
)


def main() -> None:
    collector = HotmartCollector()
    portfolio_service = DiscoveryPortfolioService()

    products = collector.search_products(
        keyword="Excel",
        country_code="BR",
        language_code="pt-BR",
        limit=10,
    )

    if not products:
        print("No discovered products were returned.")
        return

    selected_product = products[0]

    print("Saving discovered product:")
    pprint(selected_product.to_dict())

    result = portfolio_service.save_to_portfolio(
        selected_product
    )

    print("\nSaved successfully:")
    pprint(result)


if __name__ == "__main__":
    main()