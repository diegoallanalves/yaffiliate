"""Revenue-focused YAffiliate dashboard."""
from __future__ import annotations
from app.services.translation_service import ui
import streamlit as st
from app.components.layout import navigate_to, page_header
from app.services.dashboard_service import DashboardService

def render() -> None:
    """Render the YAffiliate command centre."""
    page_header('Command Centre', 'Turn research into campaigns that can make money.', 'Focus on the highest-value actions: find opportunities, build campaigns, test them, and track what deserves more investment.')
    user_id = st.session_state.get('auth_user_id')
    if not user_id:
        st.error(ui('Your authenticated user ID could not be found. Please sign in again.'))
        return
    try:
        dashboard_service = DashboardService(user_id=str(user_id))
        snapshot = dashboard_service.get_snapshot()
    except Exception as error:
        st.error(ui('Dashboard data could not be loaded.'))
        st.exception(error)
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(ui('Products researched'), len(snapshot.products))
    c2.metric(ui('Saved campaigns'), snapshot.campaign_count)
    c3.metric(ui('Modelled profit'), f'R$ {snapshot.modelled_profit:,.2f}')
    c4.metric(ui('Average ROAS'), f'{snapshot.average_roas:.2f}x')
    st.divider()
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader(ui('Recent campaigns'))
        if not snapshot.campaigns:
            st.info(ui('Generate your first campaign to see it here.'))
        else:
            for campaign in snapshot.campaigns:
                name = dashboard_service.campaign_display_name(campaign)
                created = str(campaign.get('created_at') or '')[:19].replace('T', ' ')
                with st.container(border=True):
                    st.markdown(f'**{name}**')
                    st.caption(f"{campaign.get('product_name', 'Product')} · {created}")
                    if st.button(ui('Open campaign'), key=f"dashboard_open_{campaign['id']}", use_container_width=True):
                        st.session_state['campaign_history_selected_id'] = campaign['id']
                        navigate_to('campaign_history')
                        st.rerun()
    with right:
        st.subheader(ui('Top opportunities'))
        if snapshot.products.empty:
            st.info(ui('Add products in Product Research.'))
        else:
            wanted = [column for column in ['name', 'network', 'opportunity_score', 'commission', 'search_volume'] if column in snapshot.products.columns]
            st.dataframe(snapshot.products.sort_values('opportunity_score', ascending=False).head(5)[wanted], hide_index=True, use_container_width=True)
    st.divider()
    st.subheader(ui('Next revenue actions'))
    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown('**1. Find an opportunity**')
        st.caption(ui('Research products before spending money on traffic.'))
        if st.button(ui('Product Discovery'), use_container_width=True):
            navigate_to('product_discovery')
            st.rerun()
    with a2:
        st.markdown('**2. Build the campaign**')
        st.caption(ui('Generate SEO, landing page, emails and Google Ads.'))
        if st.button(ui('Quick Generate'), use_container_width=True):
            navigate_to('quick_generate')
            st.rerun()
    with a3:
        st.markdown('**3. Review saved work**')
        st.caption(ui('Reopen campaigns and continue from where you stopped.'))
        if st.button(ui('Campaign History'), use_container_width=True):
            navigate_to('campaign_history')
            st.rerun()
