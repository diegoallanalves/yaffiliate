from __future__ import annotations

import os
from html import escape

from dotenv import load_dotenv

load_dotenv()


def _template_copy(product_name: str, audience: str, benefit: str, cta: str) -> dict[str, str]:
    safe_product = escape(product_name)
    safe_audience = escape(audience)
    safe_benefit = escape(benefit)
    safe_cta = escape(cta)

    return {
        "headline": f"Discover how {safe_product} can help you achieve {safe_benefit}",
        "subheadline": f"A practical option designed for {safe_audience}.",
        "body": (
            f"Explore the product details, assess whether it fits your needs, "
            f"and review the official offer before purchasing. This page is an "
            f"independent affiliate presentation and may earn a commission."
        ),
        "cta": safe_cta,
    }


def generate_landing_copy(
    product_name: str,
    audience: str,
    benefit: str,
    cta: str,
) -> dict[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _template_copy(product_name, audience, benefit, cta)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        prompt = f'''
Create concise, truthful affiliate landing-page copy.

Product: {product_name}
Audience: {audience}
Main benefit: {benefit}
CTA: {cta}

Rules:
- Do not invent testimonials, results, discounts, certifications, urgency, or guarantees.
- Avoid medical, financial, or income promises.
- Make the affiliate nature transparent.
- Return exactly four lines:
HEADLINE:
SUBHEADLINE:
BODY:
CTA:
'''
        response = client.responses.create(model=model, input=prompt)
        text = response.output_text.strip()

        parsed: dict[str, str] = {}
        for line in text.splitlines():
            for key in ("HEADLINE", "SUBHEADLINE", "BODY", "CTA"):
                prefix = f"{key}:"
                if line.upper().startswith(prefix):
                    parsed[key.lower()] = line[len(prefix):].strip()

        required = {"headline", "subheadline", "body", "cta"}
        return parsed if required.issubset(parsed) else _template_copy(
            product_name, audience, benefit, cta
        )
    except Exception:
        return _template_copy(product_name, audience, benefit, cta)
