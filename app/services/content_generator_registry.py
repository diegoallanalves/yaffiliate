from __future__ import annotations

from typing import Any

from app.models.discovery_product import DiscoveryProduct
from app.models.product_analysis import ProductAnalysis
from app.services.base_content_generator import (
    BaseContentGenerator,
)
from app.services.landing_page_service import (
    LandingPageService,
)
from app.services.seo_article_service import (
    SEOArticleService,
)


class ContentGeneratorRegistry:
    """
    Central registry for Content Studio generators.

    Registry:
    A central place that stores and retrieves available
    content generators.

    Every registered generator follows the
    BaseContentGenerator contract.

    This means the registry does not need separate
    if/elif conditions for every content type.
    """

    def __init__(self) -> None:
        self._generators: dict[
            str,
            BaseContentGenerator,
        ] = {
            "seo_article": SEOArticleService(),
            "landing_page": LandingPageService(),
        }

    def get(
        self,
        generator_key: str,
    ) -> BaseContentGenerator | None:
        """
        Return a generator using its registered key.
        """
        cleaned_key = (
            generator_key.strip().casefold()
        )

        return self._generators.get(
            cleaned_key
        )

    def register(
        self,
        *,
        generator_key: str,
        generator: BaseContentGenerator,
    ) -> None:
        """
        Register or replace a content generator.

        Future examples:
        - landing_page
        - email_sequence
        - google_ads
        - product_review
        """
        cleaned_key = (
            generator_key.strip().casefold()
        )

        if not cleaned_key:
            raise ValueError(
                "Generator key cannot be empty."
            )

        if not isinstance(
            generator,
            BaseContentGenerator,
        ):
            raise TypeError(
                (
                    "Generator must inherit from "
                    "BaseContentGenerator."
                )
            )

        self._generators[
            cleaned_key
        ] = generator

    def unregister(
        self,
        generator_key: str,
    ) -> bool:
        """
        Remove a generator from the registry.

        Returns True when a generator was removed.
        Returns False when the key did not exist.
        """
        cleaned_key = (
            generator_key.strip().casefold()
        )

        if cleaned_key not in self._generators:
            return False

        del self._generators[
            cleaned_key
        ]

        return True

    def is_available(
        self,
        generator_key: str,
    ) -> bool:
        """
        Check whether a generator is registered.
        """
        return self.get(
            generator_key
        ) is not None

    def list_available_keys(
        self,
    ) -> list[str]:
        """
        Return all registered generator keys.
        """
        return sorted(
            self._generators.keys()
        )

    def generate(
        self,
        *,
        generator_key: str,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        field_values: dict[str, Any],
    ) -> Any:
        """
        Run the selected content generator.

        kwargs = keyword arguments.

        Keyword arguments allow every generator to receive
        its own settings without changing this registry.

        Examples:
        - SEO article: keyword, tone and length
        - Landing page: target audience, CTA and tone
        - Email sequence: email count and tone

        SEO = Search Engine Optimization.
        CTA = Call to Action.
        """
        generator = self.get(
            generator_key
        )

        if generator is None:
            raise ValueError(
                (
                    "The selected content generator "
                    "is not available: "
                    f"{generator_key}"
                )
            )

        cleaned_field_values = {
            str(key): value
            for key, value in field_values.items()
            if value is not None
        }

        return generator.generate(
            product=product,
            analysis=analysis,
            **cleaned_field_values,
        )