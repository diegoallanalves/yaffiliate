from __future__ import annotations

from collections.abc import Iterable

from app.collectors.base_collector import BaseCollector
from app.collectors.hotmart_collector import HotmartCollector
from app.models.discovery_product import DiscoveryProduct


class ProductDiscoveryService:
    """
    Coordinates affiliate-network collectors and returns
    standardised discovery results sorted by opportunity score.
    """

    def __init__(
        self,
        collectors: Iterable[BaseCollector] | None = None,
    ) -> None:
        self.collectors = list(
            collectors or [HotmartCollector()]
        )

    def search(
        self,
        *,
        keyword: str,
        selected_networks: list[str] | None = None,
        country_code: str | None = None,
        language_code: str | None = None,
        limit_per_network: int = 20,
    ) -> list[DiscoveryProduct]:
        cleaned_keyword = keyword.strip()

        if not cleaned_keyword:
            return []

        network_filter = {
            network.strip().lower()
            for network in (selected_networks or [])
            if network.strip()
        }

        results: list[DiscoveryProduct] = []

        for collector in self.collectors:
            collector_name = collector.network_name.strip().lower()

            if (
                network_filter
                and collector_name not in network_filter
            ):
                continue

            products = collector.search_products(
                keyword=cleaned_keyword,
                country_code=country_code,
                language_code=language_code,
                limit=limit_per_network,
            )

            results.extend(products)

        results.sort(
            key=lambda product: product.opportunity_score,
            reverse=True,
        )

        return results

    def list_available_networks(self) -> list[str]:
        return sorted(
            {
                collector.network_name
                for collector in self.collectors
            }
        )