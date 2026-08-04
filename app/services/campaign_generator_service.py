"""Generate a coordinated Filtrify marketing campaign.

This campaign version combines existing, tested generators:

- Search Engine Optimization article
- Landing page
- Email sequence
- Google Ads campaign

Future versions can add social-media and additional advertising assets without
changing the existing generators.

SEO means Search Engine Optimization.
CTA means Call to Action.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.models.discovery_product import (
    DiscoveryProduct,
)
from app.models.email_sequence import (
    EmailSequence,
)
from app.models.google_ads_campaign import (
    GoogleAdsAsset,
)
from app.models.landing_page import (
    LandingPage,
)
from app.models.product_analysis import (
    ProductAnalysis,
)
from app.models.seo_article import (
    SEOArticle,
)
from app.services.email_sequence_service import (
    EmailSequenceService,
)
from app.services.google_ads_service import (
    GoogleAdsService,
)
from app.services.landing_page_service import (
    LandingPageService,
)
from app.services.seo_article_service import (
    SEOArticleService,
)


@dataclass(frozen=True, slots=True)
class CampaignPackage:
    """Represent the assets generated for one campaign.

    Attributes:
        campaign_name:
            Human-readable campaign name.

        product_name:
            Product used to create the campaign.

        seo_article:
            Generated Search Engine Optimization article.

        landing_page:
            Generated landing-page copy.

        email_sequence:
            Generated coordinated email campaign.

        google_ads:
            Generated Google Ads campaign assets.

        target_keyword:
            Primary keyword used throughout the campaign.

        target_audience:
            Audience used throughout the campaign.

        tone:
            Shared writing tone.

        created_at:
            Coordinated Universal Time creation timestamp.
    """

    campaign_name: str
    product_name: str

    seo_article: SEOArticle
    landing_page: LandingPage
    email_sequence: EmailSequence
    google_ads: GoogleAdsAsset

    target_keyword: str
    target_audience: str
    tone: str

    created_at: datetime

    @property
    def total_estimated_words(self) -> int:
        """Return the combined estimated word count.

        Google Ads are short advertising assets and are included using their
        plain-text representation.
        """

        google_ads_word_count = len(
            self.google_ads.to_plain_text().split()
        )

        return (
            self.seo_article.estimated_word_count
            + self.landing_page.estimated_word_count
            + self.email_sequence.total_estimated_words
            + google_ads_word_count
        )

    @property
    def average_quality_score(self) -> float:
        """Return the average score of scored campaign assets.

        The email sequence and Google Ads campaign do not currently have
        dedicated quality scores. This calculation therefore uses the Search
        Engine Optimization score and landing-page conversion score.
        """

        return round(
            (
                self.seo_article.seo_score
                + self.landing_page.conversion_score
            )
            / 2,
            1,
        )

    @property
    def asset_count(self) -> int:
        """Return the number of generated campaign assets."""

        return 4


class CampaignGeneratorService:
    """Generate a coordinated campaign from product intelligence.

    The service orchestrates existing generators instead of duplicating their
    business logic.
    """

    VALID_TONES = {
        "Professional",
        "Friendly",
        "Persuasive",
        "Educational",
    }

    VALID_ARTICLE_LENGTHS = {
        "Short",
        "Medium",
        "Long",
    }

    MINIMUM_EMAIL_COUNT = 3
    MAXIMUM_EMAIL_COUNT = 5

    def __init__(
        self,
        *,
        seo_article_service: SEOArticleService | None = None,
        landing_page_service: LandingPageService | None = None,
        email_sequence_service: EmailSequenceService | None = None,
        google_ads_service: GoogleAdsService | None = None,
    ) -> None:
        """Initialize the campaign generator.

        Optional service arguments make this class easier to test.
        """

        self._seo_article_service = (
            seo_article_service
            or SEOArticleService()
        )

        self._landing_page_service = (
            landing_page_service
            or LandingPageService()
        )

        self._email_sequence_service = (
            email_sequence_service
            or EmailSequenceService()
        )

        self._google_ads_service = (
            google_ads_service
            or GoogleAdsService()
        )

    def generate(
        self,
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
        target_keyword: str | None = None,
        target_audience: str | None = None,
        tone: str = "Professional",
        article_length: str = "Medium",
        primary_goal: str = "Visit Sales Page",
        email_count: int = 3,
        campaign_name: str | None = None,
    ) -> CampaignPackage:
        """Generate one coordinated marketing campaign.

        Args:
            product:
                Product selected for promotion.

            analysis:
                Product-intelligence analysis used by the generators.

            target_keyword:
                Main Search Engine Optimization and advertising keyword. The
                product name is used when this value is omitted.

            target_audience:
                Audience used throughout the campaign. The analysis audience
                is used when this value is omitted.

            tone:
                Shared writing tone.

            article_length:
                Desired Search Engine Optimization article length.

            primary_goal:
                Main conversion goal for the landing page, email sequence, and
                Google Ads campaign.

            email_count:
                Number of campaign emails to generate. Supported values are
                three to five.

            campaign_name:
                Optional campaign name.

        Returns:
            A CampaignPackage containing all generated assets.
        """

        self._validate_inputs(
            product=product,
            analysis=analysis,
        )

        resolved_keyword = self._resolve_keyword(
            product=product,
            target_keyword=target_keyword,
        )

        resolved_audience = self._resolve_audience(
            analysis=analysis,
            target_audience=target_audience,
        )

        resolved_tone = self._resolve_tone(
            tone
        )

        resolved_article_length = (
            self._resolve_article_length(
                article_length
            )
        )

        resolved_email_count = (
            self._resolve_email_count(
                email_count
            )
        )

        resolved_campaign_name = (
            self._resolve_campaign_name(
                product=product,
                campaign_name=campaign_name,
            )
        )

        seo_article = (
            self._seo_article_service.generate(
                product=product,
                analysis=analysis,
                target_keyword=resolved_keyword,
                tone=resolved_tone,
                length=resolved_article_length,
            )
        )

        landing_page = (
            self._landing_page_service.generate(
                product=product,
                analysis=analysis,
                target_audience=resolved_audience,
                primary_goal=primary_goal,
                tone=resolved_tone,
            )
        )

        email_sequence = (
            self._email_sequence_service.generate(
                product=product,
                analysis=analysis,
                target_audience=resolved_audience,
                tone=resolved_tone,
                email_count=resolved_email_count,
                primary_goal=primary_goal,
                sequence_name=(
                    f"{resolved_campaign_name} "
                    "Email Sequence"
                ),
            )
        )

        google_ads = (
            self._google_ads_service.generate(
                product=product,
                analysis=analysis,
                target_keyword=resolved_keyword,
                target_audience=resolved_audience,
                tone=resolved_tone,
                primary_goal=primary_goal,
                campaign_name=(
                    f"{resolved_campaign_name} "
                    "Google Ads"
                ),
            )
        )

        return CampaignPackage(
            campaign_name=resolved_campaign_name,
            product_name=product.product_name,
            seo_article=seo_article,
            landing_page=landing_page,
            email_sequence=email_sequence,
            google_ads=google_ads,
            target_keyword=resolved_keyword,
            target_audience=resolved_audience,
            tone=resolved_tone,
            created_at=datetime.now(
                timezone.utc
            ),
        )

    @staticmethod
    def _validate_inputs(
        *,
        product: DiscoveryProduct,
        analysis: ProductAnalysis,
    ) -> None:
        """Validate the required campaign inputs."""

        if not isinstance(
            product,
            DiscoveryProduct,
        ):
            raise TypeError(
                "product must be a DiscoveryProduct instance."
            )

        if not isinstance(
            analysis,
            ProductAnalysis,
        ):
            raise TypeError(
                "analysis must be a ProductAnalysis instance."
            )

    @staticmethod
    def _resolve_keyword(
        *,
        product: DiscoveryProduct,
        target_keyword: str | None,
    ) -> str:
        """Resolve the primary campaign keyword."""

        if (
            target_keyword
            and target_keyword.strip()
        ):
            return target_keyword.strip()

        product_name = (
            product.product_name.strip()
        )

        if not product_name:
            raise ValueError(
                "The selected product has no product name."
            )

        return product_name

    @staticmethod
    def _resolve_audience(
        *,
        analysis: ProductAnalysis,
        target_audience: str | None,
    ) -> str:
        """Resolve the shared campaign audience."""

        if (
            target_audience
            and target_audience.strip()
        ):
            return target_audience.strip()

        audience_items = [
            str(item).strip()
            for item in analysis.target_audience
            if str(item).strip()
        ]

        if audience_items:
            return ", ".join(
                audience_items
            )

        return "people interested in this product"

    def _resolve_tone(
        self,
        tone: str,
    ) -> str:
        """Validate and normalize the shared campaign tone."""

        cleaned_tone = (
            tone.strip().title()
            if tone
            else "Professional"
        )

        if cleaned_tone not in self.VALID_TONES:
            return "Professional"

        return cleaned_tone

    def _resolve_article_length(
        self,
        article_length: str,
    ) -> str:
        """Validate and normalize the article length."""

        cleaned_length = (
            article_length.strip().title()
            if article_length
            else "Medium"
        )

        if (
            cleaned_length
            not in self.VALID_ARTICLE_LENGTHS
        ):
            return "Medium"

        return cleaned_length

    def _resolve_email_count(
        self,
        email_count: int,
    ) -> int:
        """Validate and normalize the requested email count."""

        try:
            resolved_count = int(
                email_count
            )
        except (
            TypeError,
            ValueError,
        ):
            return self.MINIMUM_EMAIL_COUNT

        return max(
            self.MINIMUM_EMAIL_COUNT,
            min(
                resolved_count,
                self.MAXIMUM_EMAIL_COUNT,
            ),
        )

    @staticmethod
    def _resolve_campaign_name(
        *,
        product: DiscoveryProduct,
        campaign_name: str | None,
    ) -> str:
        """Resolve the campaign display name."""

        if (
            campaign_name
            and campaign_name.strip()
        ):
            return campaign_name.strip()

        return (
            f"{product.product_name} "
            "Affiliate Campaign"
        )