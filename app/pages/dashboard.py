"""Revenue-focused YAffiliate dashboard."""

from __future__ import annotations

import streamlit as st

from app.components.layout import navigate_to, page_header
from app.services.dashboard_service import DashboardService


def render() -> None:
    """Render the YAffiliate command centre."""

    page_header(
        "Command Centre",
        "Turn research into campaigns that can make money.",
        (
            "Focus on the highest-value actions: find opportunities, "
            "build campaigns, test them, and track what deserves more investment."
        ),
    )

    # Get the authenticated Supabase UUID stored during sign-in.
    user_id = st.session_state.get("auth_user_id")

    if not user_id:
        st.error(
            "Your authenticated user ID could not be found. "
            "Please sign in again."
        )
        return

    # Create the dashboard service at render time using
    # the authenticated user's real UUID.
    try:
        dashboard_service = DashboardService(
            user_id=str(user_id)
        )
        snapshot = dashboard_service.get_snapshot()

    except Exception as error:
        st.error("Dashboard data could not be loaded.")
        st.exception(error)
        return

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Products researched",
        len(snapshot.products),
    )

    c2.metric(
        "Saved campaigns",
        snapshot.campaign_count,
    )

    c3.metric(
        "Modelled profit",
        f"R$ {snapshot.modelled_profit:,.2f}",
    )

    c4.metric(
        "Average ROAS",
        f"{snapshot.average_roas:.2f}x",
    )

    st.divider()

    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Recent campaigns")

        if not snapshot.campaigns:
            st.info(
                "Generate your first campaign to see it here."
            )

        else:
            for campaign in snapshot.campaigns:
                name = dashboard_service.campaign_display_name(
                    campaign
                )

                created = (
                    str(campaign.get("created_at") or "")[:19]
                    .replace("T", " ")
                )

                with st.container(border=True):
                    st.markdown(f"**{name}**")

                    st.caption(
                        f'{campaign.get("product_name", "Product")} '
                        f'· {created}'
                    )

                    if st.button(
                        "Open campaign",
                        key=f'dashboard_open_{campaign["id"]}',
                        use_container_width=True,
                    ):
                        st.session_state[
                            "campaign_history_selected_id"
                        ] = campaign["id"]

                        navigate_to("campaign_history")
                        st.rerun()

    with right:
        st.subheader("Top opportunities")

        if snapshot.products.empty:
            st.info(
                "Add products in Product Research."
            )

        else:
            wanted = [
                column
                for column in [
                    "name",
                    "network",
                    "opportunity_score",
                    "commission",
                    "search_volume",
                ]
                if column in snapshot.products.columns
            ]

            st.dataframe(
                snapshot.products
                .sort_values(
                    "opportunity_score",
                    ascending=False,
                )
                .head(5)[wanted],
                hide_index=True,
                use_container_width=True,
            )

    st.divider()

    st.subheader("Next revenue actions")

    a1, a2, a3 = st.columns(3)

    with a1:
        st.markdown(
            "**1. Find an opportunity**"
        )

        st.caption(
            "Research products before spending money on traffic."
        )

        if st.button(
            "Product Discovery",
            use_container_width=True,
        ):
            navigate_to("product_discovery")
            st.rerun()

    with a2:
        st.markdown(
            "**2. Build the campaign**"
        )

        st.caption(
            "Generate SEO, landing page, emails and Google Ads."
        )

        if st.button(
            "Quick Generate",
            use_container_width=True,
        ):
            navigate_to("quick_generate")
            st.rerun()

    with a3:
        st.markdown(
            "**3. Review saved work**"
        )

        st.caption(
            "Reopen campaigns and continue from where you stopped."
        )

        if st.button(
            "Campaign History",
            use_container_width=True,
        ):
            navigate_to("campaign_history")
            st.rerun()