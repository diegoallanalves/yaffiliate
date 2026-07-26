from app.repositories.product_repository import ProductRepository


def main() -> None:
    repo = ProductRepository()

    product_id = repo.create_product(
        product_name="Test Excel Course",
        category="Education",
        language_code="pt-BR",
        country_code="BR",
        price=297,
        commission_amount=150,
        commission_percent=50,
        status="Research",
        notes="Temporary repository integration test.",
    )

    print("Created product:", product_id)

    product = repo.get_product(product_id)
    print("Product:", product)

    repo.add_product_metric(
        product_id=product_id,
        epc=2.5,
        search_volume=5000,
        competition_score=45,
        estimated_cpc=1.8,
        google_trend_score=70,
        refund_rate=5,
        opportunity_score=72,
        data_source="Manual test",
    )

    latest_metric = repo.get_latest_product_metric(product_id)
    print("Latest metric:", latest_metric)

    products = repo.list_products()
    print("Number of products:", len(products))

    updated = repo.update_product(
        product_id,
        status="Testing",
        notes="Repository update test completed.",
    )
    print("Updated:", updated)

    updated_product = repo.get_product(product_id)
    print("Updated product:", updated_product)

    deleted = repo.delete_product(product_id)
    print("Deleted:", deleted)


if __name__ == "__main__":
    main()