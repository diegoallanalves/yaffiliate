from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.models.product_analysis import ProductAnalysis


class BaseContentGenerator(ABC):
    """
    Base contract for every content generator.

    ABC = Abstract Base Class.

    An abstract base class defines rules that child classes
    must follow. In this case, every content generator must
    provide a generate() method.

    Examples of future generators:
    - SEO = Search Engine Optimization article generator
    - Landing page generator
    - Email sequence generator
    - Google Ads generator
    - YouTube script generator
    """

    @abstractmethod
    def generate(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        **kwargs: Any,
    ) -> Any:
        """
        Generate content for one product.

        Each child generator decides:
        - which additional inputs it needs;
        - which output model it returns;
        - how the content is created.
        """
        raise NotImplementedError