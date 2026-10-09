"""Private Growth Dashboard for the YAffiliate owner."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.layout import page_header
from app.services.admin_service import AdminService
from app.services.growth_analytics_service import (
    GrowthAnalyticsService,
)


def render() -> None:
    """Render private YAffiliate growth analytics."""

    if not AdminService.is_admin():
        st.error("You do not have access to this page.")
        return

    page_header(
        "Owner Analytics",
        "Growth Dashboard",
        "Track the YAffiliate customer funnel and growth.",
    )

    try:
        service = GrowthAnalyticsService()

        metrics = service.get_funnel_metrics()
        sources = service.get_acquisition_sources()
        events = service.get_events(limit=100)

    except Exception as error:
        st.error("Growth analytics could not be loaded.")
        st.exception(error)
        return

    st.subheader("Customer Funnel")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Signups",
        metrics["signups"],
    )

    c2.metric(
        "Campaign Users",
        metrics["campaign_users"],
        f'{metrics["signup_to_campaign"]:.1f}% of signups',
    )

    c3.metric(
        "Upgrade Clicks",
        metrics["upgrade_users"],
        f'{metrics["campaign_to_upgrade"]:.1f}% of campaign users',
    )

    c4.metric(
        "Paid Customers",
        metrics["paid_customers"],
        f'{metrics["signup_to_paid"]:.1f}% of signups',
    )

    st.divider()

    st.subheader("Conversion Rates")

    r1, r2, r3 = st.columns(3)

    r1.metric(
        "Signup → Campaign",
        f'{metrics["signup_to_campaign"]:.1f}%',
    )

    r2.metric(
        "Campaign → Upgrade",
        f'{metrics["campaign_to_upgrade"]:.1f}%',
    )

    r3.metric(
        "Upgrade → Paid",
        f'{metrics["upgrade_to_paid"]:.1f}%',
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Activity")

        st.metric(
            "Campaigns Generated",
            metrics["campaign_events"],
        )

        st.metric(
            "Upgrade Clicks",
            metrics["upgrade_events"],
        )

        st.metric(
            "Subscriptions Started",
            metrics["subscription_events"],
        )

    with right:
        st.subheader("Acquisition Sources")

        if sources:
            source_df = pd.DataFrame(sources)

            st.dataframe(
                source_df,
                hide_index=True,
                use_container_width=True,
            )

        else:
            st.info("No acquisition-source data yet.")

    st.divider()

    st.subheader("Recent Growth Events")

    if not events:
        st.info("No growth events recorded yet.")
        return

    event_df = pd.DataFrame(events)

    wanted_columns = [
        column
        for column in [
            "created_at",
            "event_name",
            "event_page",
            "utm_source",
            "utm_campaign",
            "user_id",
        ]
        if column in event_df.columns
    ]

    st.dataframe(
        event_df[wanted_columns],
        hide_index=True,
        use_container_width=True,
    )