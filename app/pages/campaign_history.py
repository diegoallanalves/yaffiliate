"""Campaign History page for Filtrify.

This page lists previously saved campaigns and allows the user to:

- review campaign metadata;
- inspect the stored campaign JSON;
- download the stored JSON file;
- delete individual campaigns;
- clear the complete campaign history.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from app.components.layout import (
    page_header,
)
from app.models.saved_campaign import (
    SavedCampaign,
)
from app.services.campaign_history_service import (
    CampaignHistoryService,
)


history_service = CampaignHistoryService()


def render() -> None:
    """Render the Filtrify Campaign History page."""

    page_header(
        "My Campaigns",
        "Access every marketing campaign you've created.",
        (
            "Review, download and manage every campaign generated with Filtrify."
        ),
    )

    saved_campaigns = (
        history_service.list_campaigns()
    )

    _render_history_summary(
        saved_campaigns
    )

    if not saved_campaigns:
        st.info(
            "No campaigns have been saved yet. "
            "Generate a campaign and use the Save Campaign button."
        )
        return

    selected_campaign_id = st.selectbox(
        "Choose a campaign",
        options=[
            campaign.campaign_id
            for campaign in saved_campaigns
        ],
        format_func=lambda campaign_id: (
            _campaign_label(
                campaign_id=campaign_id,
                campaigns=saved_campaigns,
            )
        ),
        key="campaign_history_selected_id",
    )

    selected_campaign = next(
        (
            campaign
            for campaign in saved_campaigns
            if (
                campaign.campaign_id
                == selected_campaign_id
            )
        ),
        None,
    )

    if selected_campaign is None:
        st.error(
            "The selected campaign could not be found."
        )
        return

    _render_campaign_metadata(
        selected_campaign
    )

    _render_campaign_data(
        selected_campaign
    )

    _render_campaign_actions(
        selected_campaign
    )

    _render_clear_history(
        saved_campaigns
    )


def _render_history_summary(
    saved_campaigns: list[SavedCampaign],
) -> None:
    """Render campaign-history summary metrics."""

    total_campaigns = len(
        saved_campaigns
    )

    total_assets = sum(
        campaign.asset_count
        for campaign in saved_campaigns
    )

    total_words = sum(
        campaign.total_estimated_words
        for campaign in saved_campaigns
    )

    average_quality = (
        round(
            sum(
                campaign.average_quality_score
                for campaign in saved_campaigns
            )
            / total_campaigns,
            1,
        )
        if total_campaigns
        else 0.0
    )

    (
        campaign_metric,
        asset_metric,
        word_metric,
        quality_metric,
    ) = st.columns(4)

    campaign_metric.metric(
        "Campaigns",
        total_campaigns,
    )

    asset_metric.metric(
        "Assets",
        total_assets,
    )

    word_metric.metric(
        "Words",
        f"{total_words:,}",
    )

    quality_metric.metric(
        "Quality",
        f"{average_quality:.1f}/100",
    )


def _render_campaign_metadata(
    campaign: SavedCampaign,
) -> None:
    """Render metadata for one saved campaign."""

    st.divider()

    st.markdown("### Campaign Overview")

    with st.expander(
            "Technical Details",
            expanded=False,
    ):
        st.code(
            campaign.campaign_id
        )

    (
        product_column,
        asset_column,
        word_column,
        quality_column,
    ) = st.columns(4)

    product_column.markdown(
        "**Product**"
    )

    product_column.write(
        campaign.product_name
    )

    asset_column.metric(
        "Assets",
        campaign.asset_count,
    )

    word_column.metric(
        "Estimated words",
        f"{campaign.total_estimated_words:,}",
    )

    quality_column.metric(
        "Quality",
        (
            f"{campaign.average_quality_score:.1f}"
            "/100"
        ),
    )

    detail_column_1, detail_column_2 = (
        st.columns(2)
    )

    with detail_column_1:
        st.markdown(
            "**Target keyword**"
        )

        st.write(
            campaign.target_keyword
        )

        st.markdown(
            "**Writing tone**"
        )

        st.write(
            campaign.tone
        )

        st.markdown(
            "**Generated**"
        )

        st.write(
            campaign.created_at.strftime(
                "%d %B %Y, %H:%M UTC"
            )
        )

    with detail_column_2:
        st.markdown(
            "**Target audience**"
        )

        st.write(
            campaign.target_audience
        )

        st.markdown(
            "**Saved**"
        )

        st.write(
            campaign.saved_at.strftime(
                "%d %B %Y, %H:%M UTC"
            )
        )

        st.markdown(
            "**Storage**"
        )

        st.write(
            "Saved locally"
        )


def _render_campaign_data(
    campaign: SavedCampaign,
) -> None:
    """Render the stored campaign JSON."""

    st.divider()

    st.subheader(
        "Campaign Files"
    )

    try:
        campaign_data = (
            history_service.load_campaign_data(
                campaign.campaign_id
            )
        )

    except Exception as error:
        st.error(
            "The saved campaign data could not be loaded. "
            f"{error}"
        )
        return

    with st.expander(
        "Developer Data",
        expanded=False,
    ):
        st.json(
            campaign_data
        )

    campaign_json = json.dumps(
        campaign_data,
        ensure_ascii=False,
        indent=2,
    )

    safe_file_name = (
        campaign.campaign_name
        .strip()
        .replace(
            " ",
            "_",
        )
    )

    st.download_button(
        label="Download Campaign JSON",
        data=campaign_json,
        file_name=(
            f"{safe_file_name}.json"
        ),
        mime="application/json",
        width="stretch",
        key=(
            "download_saved_campaign_"
            f"{campaign.campaign_id}"
        ),
    )


def _render_campaign_actions(
    campaign: SavedCampaign,
) -> None:
    """Render actions for one saved campaign."""

    st.divider()

    st.subheader(
        "Manage Campaign"
    )

    delete_campaign = st.button(
        "Delete Campaign",
        type="secondary",
        width="stretch",
        key=(
            "delete_saved_campaign_"
            f"{campaign.campaign_id}"
        ),
    )

    if not delete_campaign:
        return

    confirmation_key = (
        "confirm_delete_saved_campaign"
    )

    st.session_state[
        confirmation_key
    ] = campaign.campaign_id

    st.warning(
        "Click the confirmation button below "
        "to permanently delete this saved campaign."
    )

    confirm_delete = st.button(
        "Confirm campaign deletion",
        type="primary",
        width="stretch",
        key=(
            "confirm_delete_campaign_"
            f"{campaign.campaign_id}"
        ),
    )

    if not confirm_delete:
        return

    try:
        deleted = (
            history_service.delete_campaign(
                campaign.campaign_id
            )
        )

    except Exception as error:
        st.error(
            "The campaign could not be deleted. "
            f"{error}"
        )
        return

    if not deleted:
        st.warning(
            "The selected campaign was not found."
        )
        return

    st.session_state.pop(
        confirmation_key,
        None,
    )

    st.success(
        "The saved campaign was deleted."
    )

    st.rerun()


def _render_clear_history(
    saved_campaigns: list[SavedCampaign],
) -> None:
    """Render the clear-history controls."""

    if not saved_campaigns:
        return

    st.divider()

    with st.expander(
        "Advanced Options",
        expanded=False,
    ):
        st.warning(
            "Clearing history permanently deletes "
            "all saved campaign files."
        )

        clear_history = st.button(
            "Delete All Campaigns",
            type="secondary",
            width="stretch",
            key="clear_all_campaign_history",
        )

        if not clear_history:
            return

        confirm_clear = st.checkbox(
            "I understand that all saved campaigns will be deleted.",
            key="confirm_clear_campaign_history",
        )

        if not confirm_clear:
            st.info(
                "Tick the confirmation box to continue."
            )
            return

        final_clear = st.button(
            "Permanently clear campaign history",
            type="primary",
            width="stretch",
            key="confirm_clear_all_campaign_history",
        )

        if not final_clear:
            return

        try:
            removed_count = (
                history_service.clear_history()
            )

        except Exception as error:
            st.error(
                "Campaign history could not be cleared. "
                f"{error}"
            )
            return

        st.success(
            f"Removed {removed_count} saved campaign(s)."
        )

        st.rerun()


def _campaign_label(
    *,
    campaign_id: str,
    campaigns: list[SavedCampaign],
) -> str:
    """Return the display label for a campaign identifier."""

    campaign = next(
        (
            item
            for item in campaigns
            if item.campaign_id == campaign_id
        ),
        None,
    )

    if campaign is None:
        return campaign_id

    return campaign.display_name