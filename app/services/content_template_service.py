from __future__ import annotations

from app.models.content_template import (
    ContentTemplate,
    ContentTemplateField,
)


class ContentTemplateService:
    """
    Provides the catalogue of AI Content Studio templates.

    Only templates with an implemented generator are enabled.
    New templates can be activated later without changing
    the Streamlit interface.
    """

    def __init__(self) -> None:
        self._templates = [
            ContentTemplate(
                template_id="seo_article",
                name="SEO Article",
                description=(
                    "Generate a complete SEO article "
                    "optimized for organic search."
                ),
                icon="📰",
                generator_key="seo_article",
                fields=[
                    ContentTemplateField(
                        name="keyword",
                        label="Target keyword",
                        required=True,
                        placeholder="Excel course",
                    ),
                    ContentTemplateField(
                        name="tone",
                        label="Writing tone",
                        field_type="select",
                        default_value="Professional",
                        options=[
                            "Professional",
                            "Friendly",
                            "Persuasive",
                            "Educational",
                        ],
                    ),
                    ContentTemplateField(
                        name="length",
                        label="Article length",
                        field_type="select",
                        default_value="Medium",
                        options=[
                            "Short",
                            "Medium",
                            "Long",
                        ],
                    ),
                ],
                enabled=True,
            ),
            ContentTemplate(
                template_id="landing_page",
                name="Landing Page",
                description=(
                    "Generate high-converting landing page copy."
                ),
                icon="🌐",
                generator_key="landing_page",
                enabled=False,
            ),
            ContentTemplate(
                template_id="email_sequence",
                name="Email Sequence",
                description=(
                    "Generate a multi-email nurturing campaign."
                ),
                icon="📧",
                generator_key="email_sequence",
                enabled=False,
            ),
            ContentTemplate(
                template_id="google_ads",
                name="Google Ads",
                description=(
                    "Generate Google Ads headlines and descriptions."
                ),
                icon="🎯",
                generator_key="google_ads",
                enabled=False,
            ),
            ContentTemplate(
                template_id="facebook_ads",
                name="Facebook Ads",
                description=(
                    "Generate Meta Ads copy."
                ),
                icon="📱",
                generator_key="facebook_ads",
                enabled=False,
            ),
            ContentTemplate(
                template_id="product_review",
                name="Product Review",
                description=(
                    "Generate a product review article."
                ),
                icon="⭐",
                generator_key="product_review",
                enabled=False,
            ),
            ContentTemplate(
                template_id="youtube_script",
                name="YouTube Script",
                description=(
                    "Generate a YouTube review script."
                ),
                icon="▶️",
                generator_key="youtube_script",
                enabled=False,
            ),
            ContentTemplate(
                template_id="instagram_post",
                name="Instagram Post",
                description=(
                    "Generate an Instagram caption."
                ),
                icon="📷",
                generator_key="instagram_post",
                enabled=False,
            ),
            ContentTemplate(
                template_id="linkedin_post",
                name="LinkedIn Post",
                description=(
                    "Generate a professional LinkedIn article."
                ),
                icon="💼",
                generator_key="linkedin_post",
                enabled=False,
            ),
            ContentTemplate(
                template_id="faq_generator",
                name="FAQ Generator",
                description=(
                    "Generate SEO-friendly FAQ sections."
                ),
                icon="❓",
                generator_key="faq_generator",
                enabled=False,
            ),
        ]

    def list_templates(
        self,
    ) -> list[ContentTemplate]:
        """
        Return only templates currently available to users.
        """
        return [
            template
            for template in self._templates
            if template.enabled
        ]

    def list_all_templates(
        self,
    ) -> list[ContentTemplate]:
        """
        Return every registered template, including disabled ones.
        """
        return list(
            self._templates
        )

    def get_template(
        self,
        template_id: str,
    ) -> ContentTemplate | None:
        """
        Return one template by its unique identifier.
        """
        cleaned_template_id = (
            template_id.strip().casefold()
        )

        for template in self._templates:
            if (
                template.template_id.casefold()
                == cleaned_template_id
            ):
                return template

        return None

    def get_enabled_template(
        self,
        template_id: str,
    ) -> ContentTemplate | None:
        """
        Return the template only when it is enabled.
        """
        template = self.get_template(
            template_id
        )

        if template is None:
            return None

        if not template.enabled:
            return None

        return template