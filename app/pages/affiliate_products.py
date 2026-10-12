
"""Supabase-backed Affiliate Products page for YAffiliate."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.layout import page_header
from app.repositories.product_repository import ProductRepository


def safe_number(value, default=0.0):
    """Convert a database value to a usable number."""
    try:
        if value is None:
            return default
        number = float(value)
        return number if pd.notna(number) else default
    except (TypeError, ValueError):
        return default


def safe_text(value, fallback="Not set"):
    """Return a readable value for optional fields."""
    if value is None:
        return fallback
    result = str(value).strip()
    return result if result else fallback


def render():
    page_header(
        "Product catalogue",
        "Manage your affiliate shortlist.",
        "Review researched, tested and active products.",
    )

    st.markdown("### Your affiliate products")
    st.caption(
        "Products saved in Product Research appear here automatically."
    )

    try:
        products = ProductRepository().list_products()
    except Exception as exc:
        st.error("Unable to load products from Supabase.")
        st.caption(str(exc))
        return

    if not products:
        st.info(
            "No products saved in your account yet. "
            "Open Product Research to add your first product."
        )
        return

    df = pd.DataFrame(products)

    search = st.text_input(
        "Search products",
        placeholder="Search by product name",
    )

    statuses = ["All"] + sorted(
        df["Status"].dropna().astype(str).unique().tolist()
    )

    selected_status = st.selectbox(
        "Filter by status",
        statuses,
    )

    if search.strip():
        df = df[
            df["ProductName"]
            .fillna("")
            .astype(str)
            .str.contains(search.strip(), case=False, regex=False)
        ]

    if selected_status != "All":
        df = df[df["Status"] == selected_status]

    st.markdown("### Catalogue overview")

    col1, col2, col3 = st.columns(3)

    scores = pd.to_numeric(
        df["OpportunityScore"], errors="coerce"
    ).dropna()

    commissions = pd.to_numeric(
        df["CommissionAmount"], errors="coerce"
    ).dropna()

    col1.metric("Products", len(df))
    col2.metric(
        "Best opportunity score",
        f"{scores.max():.1f}/100" if not scores.empty else "Not scored",
    )
    col3.metric(
        "Average commission",
        f"R$ {commissions.mean():,.2f}"
        if not commissions.empty else "Not available",
    )

    st.divider()

    if df.empty:
        st.info("No products match your filters.")
        return

    df = df.copy()
    df["_score"] = pd.to_numeric(
        df["OpportunityScore"], errors="coerce"
    )
    df = df.sort_values("_score", ascending=False, na_position="last")

    st.markdown("### Your product shortlist")

    for product in df.to_dict("records"):
        name = safe_text(product.get("ProductName"), "Unnamed product")
        status = safe_text(product.get("Status"), "Research")
        network = safe_text(
            product.get("NetworkName"), "Network not set"
        )
        category = safe_text(
            product.get("Category"), "Category not set"
        )

        commission = safe_number(product.get("CommissionAmount"))
        volume = safe_number(product.get("SearchVolume"))
        score_value = product.get("OpportunityScore")
        score = safe_number(score_value)

        with st.container(border=True):
            st.markdown(f"#### {name}")
            st.caption(f"{network} · {category} · {status}")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Opportunity score",
                f"{score:.1f}/100"
                if pd.notna(score_value) and score_value is not None
                else "Not scored",
            )
            c2.metric("Commission per sale", f"R$ {commission:,.2f}")
            c3.metric("Search volume", f"{volume:,.0f}")

            if score_value is not None and pd.notna(score_value):
                st.progress(min(max(score / 100, 0.0), 1.0))

            with st.expander("Product details"):
                st.write(
                    f"**Estimated CPC:** "
                    f"R$ {safe_number(product.get('EstimatedCPC')):,.2f}"
                )
                st.write(
                    f"**Commission rate:** "
                    f"{safe_number(product.get('CommissionPercent')):.2f}%"
                )

                affiliate_url = safe_text(
                    product.get("AffiliateURL"), ""
                )

                if affiliate_url.startswith(("https://", "http://")):
                    st.link_button("Open affiliate link", affiliate_url)
                else:
                    st.caption("No affiliate link saved yet.")

                notes = safe_text(product.get("Notes"), "")
                if notes:
                    st.write("**Notes:**")
                    st.write(notes)

            st.caption(
                "Opportunity scores are estimates, "
                "not guaranteed sales or earnings."
            )
