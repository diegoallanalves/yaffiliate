"""Campaign History page for YAffiliate (Supabase)."""

from __future__ import annotations

import json
import re

import streamlit as st

from app.components.layout import navigate_to, page_header
from app.services.campaign_history_supabase_service import (
    CampaignHistorySupabaseService,
)


def render() -> None:
    page_header(
        "My Campaigns",
        "Access every marketing campaign you've created.",
        "Review, open, download and manage campaigns generated with YAffiliate.",
    )

    # The authenticated Supabase UUID is stored when the user signs in.
    user_id = st.session_state.get("auth_user_id")

    if not user_id:
        st.error("Your authenticated user ID could not be found. Please sign in again.")
        return

    # Create the history service only when the page is rendered,
    # using the authenticated user's real Supabase UUID.
    try:
        history_service = CampaignHistorySupabaseService(
            user_id=str(user_id)
        )
        campaigns = history_service.list_campaigns()
    except Exception as error:
        st.error("Campaign history could not be loaded.")
        st.exception(error)
        return

    if not campaigns:
        st.info("You have no saved campaigns yet.")
        return

    st.columns(4)[0].metric("Campaigns", len(campaigns))

    campaign_ids = [campaign["id"] for campaign in campaigns]

    selected_campaign_id = st.selectbox(
        "Choose a campaign",
        campaign_ids,
        format_func=lambda campaign_id: _campaign_label(
            campaign_id,
            campaigns,
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
        selected_campaign.get("product_name", ""),
    )

    st.write(
        "**Created:**",
        selected_campaign.get("created_at", ""),
    )

    try:
        campaign_data = history_service.load_campaign_data(
            selected_campaign_id
        )
    except Exception as error:
        st.error("This campaign could not be opened.")
        st.exception(error)
        return

    with st.expander("Campaign JSON", expanded=False):
        st.json(campaign_data)

    campaign_json = json.dumps(
        campaign_data,
        indent=2,
        ensure_ascii=False,
    )

    safe_name = _safe_file_name(
        selected_campaign.get(
            "product_name",
            "campaign",
        )
    )

    st.download_button(
        "Download JSON",
        campaign_json,
        file_name=f"{safe_name}.json",
        mime="application/json",
        use_container_width=True,
        key=f"download_campaign_{selected_campaign_id}",
    )

    if st.button(
        "📂 Open Campaign",
        type="primary",
        use_container_width=True,
        key=f"open_campaign_{selected_campaign_id}",
    ):
        st.session_state["loaded_campaign"] = campaign_data
        st.session_state["loaded_campaign_id"] = selected_campaign_id

        st.session_state.pop(
            "generated_campaign",
            None,
        )

        navigate_to("campaign_generator")
        st.rerun()

    if st.button(
        "Delete Campaign",
        use_container_width=True,
        key=f"delete_campaign_{selected_campaign_id}",
    ):
        try:
            history_service.delete_campaign(
                selected_campaign_id
            )

            st.session_state.pop(
                "loaded_campaign",
                None,
            )

            st.session_state.pop(
                "loaded_campaign_id",
                None,
            )

            st.success("Campaign deleted.")
            st.rerun()

        except Exception as error:
            st.exception(error)

    with st.expander(
        "Advanced",
        expanded=False,
    ):
        if st.button(
            "Delete ALL Campaigns",
            use_container_width=True,
            key="delete_all_campaigns",
        ):
            try:
                history_service.clear_history()

                st.session_state.pop(
                    "loaded_campaign",
                    None,
                )

                st.session_state.pop(
                    "loaded_campaign_id",
                    None,
                )

                st.success("History cleared.")
                st.rerun()

            except Exception as error:
                st.exception(error)


def _campaign_label(
    campaign_id: str,
    campaigns: list[dict],
) -> str:
    campaign = next(
        (
            item
            for item in campaigns
            if item["id"] == campaign_id
        ),
        None,
    )

    if not campaign:
        return campaign_id

    product = campaign.get(
        "product_name",
        "Campaign",
    )

    created = str(
        campaign.get(
            "created_at",
            "",
        )
    )[:19]

    return f"{product} - {created}"


def _safe_file_name(value: str) -> str:
    cleaned = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        value.strip(),
    )

    return (
        re.sub(r"_+", "_", cleaned).strip("_")
        or "yaffiliate_campaign"
    )