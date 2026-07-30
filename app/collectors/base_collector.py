from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.discovery_product import DiscoveryProduct


class BaseCollector(ABC):
    """
    Common interface for all affiliate-network collectors.
    """

    network_name: str

    @abstractmethod
    def search_products(
        self,
        *,
        keyword: str,
        country_code: str | None = None,
        language_code: str | None = None,
        limit: int = 20,
    ) -> list[DiscoveryProduct]:
        """
        Search the affiliate network and return standardised products.
        """
        raise NotImplementedError