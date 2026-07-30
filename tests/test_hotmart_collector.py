from pprint import pprint

from app.collectors.hotmart_collector import HotmartCollector


def main() -> None:
    collector = HotmartCollector()

    products = collector.search_products(
        keyword="Excel",
        country_code="BR",
        language_code="pt-BR",
        limit=10,
    )

    print("Products found:", len(products))

    for product in products:
        pprint(product.to_dict())


if __name__ == "__main__":
    main()