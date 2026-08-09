"""Campaign History page for YAffiliate (Supabase)."""

from __future__ import annotations

import json

import streamlit as st

from app.components.layout import page_header
from app.services.campaign_history_supabase_service import (
    CampaignHistorySupabaseService,
)


history_service = CampaignHistorySupabaseService()


def render() -> None:
    """Render the YAffiliate Campaign History page."""

    page_header(
        "My Campaigns",
        "Access every marketing campaign you've created.",
        "Review, download and manage every campaign generated with YAffiliate.",
    )

    campaigns = history_service.list_campaigns()

    if not campaigns:
        st.info("No saved campaigns found.")
        return

    st.columns(4)[0].metric(
        "Campaigns",
        len(campaigns),
    )

    campaign_ids = [
        campaign["id"]
        for campaign in campaigns
    ]

    selected_campaign_id = st.selectbox(
        "Choose a campaign",
        campaign_ids,
        format_func=lambda campaign_id: next(
            (
                (
                    f'{campaign["product_name"]} - '
                    f'{campaign["created_at"][:19]}'
                )
                for campaign in campaigns
                if campaign["id"] == campaign_id
            ),
            campaign_id,
        ),
        key="campaign_history_selected_id",
    )

    selected_campaign = next(
        campaign
        for campaign in campaigns
        if campaign["id"] == selected_campaign_id
    )

    st.subheader("Overview")

    st.write(
        "**Product:**",
        selected_campaign["product_name"],
    )

    st.write(
        "**Created:**",
        selected_campaign["created_at"],
    )

    st.write(
        "**User:**",
        selected_campaign["user_id"],
    )

    campaign_data = history_service.load_campaign_data(
        selected_campaign_id
    )

    with st.expander(
        "Campaign JSON",
        expanded=False,
    ):
        st.json(campaign_data)

    campaign_json = json.dumps(
        campaign_data,
        indent=2,
        ensure_ascii=False,
    )

    safe_file_name = (
        selected_campaign["product_name"]
        .strip()
        .replace(" ", "_")
    )

    st.download_button(
        "Download JSON",
        campaign_json,
        file_name=f"{safe_file_name}.json",
        mime="application/json",
        use_container_width=True,
        key=f"download_campaign_{selected_campaign_id}",
    )

    if st.button(
            "📂 Open Campaign",
            use_container_width=True,
            key=f"open_campaign_{selected_campaign_id}",
    ):
        st.session_state["loaded_campaign"] = campaign_data
        st.session_state["loaded_campaign_id"] = selected_campaign_id

        st.session_state["selected_route"] = "campaign_generator"
        st.rerun()

    if st.button(
        "Delete Campaign",
        use_container_width=True,
        key=f"delete_campaign_{selected_campaign_id}",
    ):
        history_service.delete_campaign(
            selected_campaign_id
        )

        st.success("Campaign deleted.")
        st.rerun()

    with st.expander(
        "Advanced",
        expanded=False,
    ):
        if st.button(
            "Delete ALL Campaigns",
            use_container_width=True,
            key="delete_all_campaigns",
        ):
            history_service.clear_history()

            st.success("History cleared.")
            st.rerun()
