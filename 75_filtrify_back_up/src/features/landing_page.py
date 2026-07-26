from __future__ import annotations

from html import escape
from pathlib import Path

from src.services.ai_service import generate_landing_copy

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "landing_pages"


def build_landing_page(
    product_name: str,
    audience: str,
    benefit: str,
    cta: str,
    affiliate_url: str,
) -> tuple[str, str]:
    copy = generate_landing_copy(product_name, audience, benefit, cta)
    safe_url = escape(affiliate_url, quote=True)
    safe_product = escape(product_name)

    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{safe_product}</title>
  <style>
    body {{ margin:0; font-family:Arial,sans-serif; background:#0f172a; color:#f8fafc; }}
    main {{ max-width:900px; margin:auto; padding:72px 24px; text-align:center; }}
    .badge {{ display:inline-block; padding:8px 12px; border:1px solid #94a3b8;
              border-radius:999px; font-size:14px; }}
    h1 {{ font-size:clamp(38px,7vw,72px); line-height:1.03; margin:24px 0; }}
    p {{ color:#cbd5e1; font-size:20px; line-height:1.6; }}
    a.cta {{ display:inline-block; margin-top:24px; padding:16px 26px;
             background:#f8fafc; color:#0f172a; text-decoration:none;
             font-weight:700; border-radius:12px; }}
    footer {{ margin-top:64px; color:#94a3b8; font-size:13px; }}
  </style>
</head>
<body>
<main>
  <span class="badge">Independent affiliate presentation</span>
  <h1>{copy["headline"]}</h1>
  <p><strong>{copy["subheadline"]}</strong></p>
  <p>{copy["body"]}</p>
  <a class="cta" href="{safe_url}" rel="nofollow sponsored noopener" target="_blank">
    {copy["cta"]}
  </a>
  <footer>
    Affiliate disclosure: this page may receive a commission when a qualifying
    purchase is made through the link. Verify all information on the official offer page.
  </footer>
</main>
</body>
</html>'''

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in product_name).strip("-")
    filename = f"{slug or 'landing-page'}.html"
    path = OUTPUT_DIR / filename
    path.write_text(html, encoding="utf-8")
    return html, str(path)
