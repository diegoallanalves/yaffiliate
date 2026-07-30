from pprint import pprint

from app.services.product_discovery_service import (
    ProductDiscoveryService,
)


def main() -> None:
    service = ProductDiscoveryService()

    print("Available networks:")
    pprint(service.list_available_networks())

    products = service.search(
        keyword="Excel",
        selected_networks=["Hotmart"],
        country_code="BR",
        language_code="pt-BR",
        limit_per_network=10,
    )

    print("\nProducts found:", len(products))

    for product in products:
        print(
            product.product_name,
            "-",
            product.opportunity_score,
        )


if __name__ == "__main__":
    main()