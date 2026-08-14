import streamlit as st

from app.bootstrap import bootstrap_app
from app.components.auth_ui import render_auth_page, render_user_sidebar
from app.components.layout import sidebar_navigation
from app.router import render_route


bootstrap_app()

if not st.session_state.get("authenticated", False):
    render_auth_page()
    st.stop()

render_user_sidebar()

route = sidebar_navigation()
render_route(route)