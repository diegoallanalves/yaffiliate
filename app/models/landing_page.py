from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LandingPageSection:
    """
    One editable section of a landing page.

    Examples:
    - Hero section
    - Benefits
    - FAQ
    - Call to Action

    FAQ = Frequently Asked Questions.

    CTA = Call to Action.
    A CTA is the prompt that encourages the visitor to take
    the next step, such as "Buy Now" or "Learn More".
    """

    section_type: str
    heading: str
    content: str
    items: list[str] = field(
        default_factory=list
    )


@dataclass(slots=True)
class LandingPage:
    """
    Structured landing-page copy for one affiliate product.

    A landing page is a focused webpage designed to persuade
    a visitor to complete one specific action.

    Typical actions include:
    - visiting the product sales page;
    - submitting an email address;
    - starting a free trial;
    - purchasing a product.
    """

    page_title: str
    meta_description: str

    product_name: str
    target_audience: str
    primary_goal: str
    tone: str

    hero_headline: str
    hero_subheadline: str
    primary_cta: str

    sections: list[LandingPageSection] = field(
        default_factory=list
    )

    final_cta_heading: str = ""
    final_cta_text: str = ""
    final_cta_button: str = ""

    estimated_word_count: int = 0
    conversion_score: float = 0.0