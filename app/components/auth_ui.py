"""Login and account creation UI for YAffiliate."""
from __future__ import annotations
from app.services.translation_service import ui
import streamlit as st
from app.services.translation_service import t
from app.services.auth_service import AuthService

def _store_auth_session(response) -> bool:
    """Persist the authenticated Supabase session across Streamlit reruns."""
    user = getattr(response, 'user', None)
    session = getattr(response, 'session', None)
    if user is None or session is None:
        return False
    access_token = getattr(session, 'access_token', None)
    refresh_token = getattr(session, 'refresh_token', None)
    if not access_token or not refresh_token:
        return False
    st.session_state['auth_user_id'] = str(user.id)
    st.session_state['auth_user_email'] = str(user.email or '')
    st.session_state['authenticated'] = True
    st.session_state['supabase_access_token'] = str(access_token)
    st.session_state['supabase_refresh_token'] = str(refresh_token)
    return True

def render_auth_page() -> None:
    auth = AuthService()
    st.title(ui('🚀 YAffiliate'))
    st.subheader(ui('AI Marketing Platform'))
    st.write(ui('Sign in to create, save and manage your affiliate campaigns.'))
    sign_in, sign_up = st.tabs([ui('Sign In'), ui('Create Account')])
    with sign_in:
        _sign_in(auth)
    with sign_up:
        _sign_up(auth)

def _sign_in(auth: AuthService) -> None:
    with st.form('auth_sign_in'):
        email = st.text_input(ui('Email'), key='signin_email')
        password = st.text_input(ui('Password'), type='password', key='signin_password')
        submitted = st.form_submit_button(ui('🔐 Sign In'), type='primary', use_container_width=True)
    if not submitted:
        return
    try:
        response = auth.sign_in(email, password)
        if not _store_auth_session(response):
            st.error(ui('Sign in did not return an authenticated session.'))
            return
        st.success(ui('Signed in successfully.'))
        st.rerun()
    except Exception as error:
        st.error(f'Sign in failed: {error}')

def _sign_up(auth: AuthService) -> None:
    with st.form('auth_sign_up'):
        email = st.text_input(ui('Email'), key='signup_email')
        password = st.text_input(ui('Password'), type='password', key='signup_password')
        confirm = st.text_input(ui('Confirm password'), type='password', key='signup_confirm')
        submitted = st.form_submit_button(ui('✨ Create Account'), type='primary', use_container_width=True)
    if not submitted:
        return
    if password != confirm:
        st.error(ui('Passwords do not match.'))
        return
    if len(password) < 8:
        st.error(ui('Password must contain at least 8 characters.'))
        return
    try:
        response = auth.sign_up(email, password)
        user = getattr(response, 'user', None)
        session = getattr(response, 'session', None)
        if user is None:
            st.error(ui('Account could not be created.'))
            return
        if session is None:
            st.success(ui('Account created. Check your email, confirm your address, then return and sign in.'))
            return
        if not _store_auth_session(response):
            st.error(ui('Account was created but the authenticated session could not be stored. Please sign in.'))
            return
        st.success(ui('Account created successfully.'))
        st.rerun()
    except Exception as error:
        st.error(f'Account creation failed: {error}')

def render_user_sidebar() -> None:
    email = st.session_state.get('auth_user_email', 'Signed-in user')
    with st.sidebar:
        st.divider()
        st.caption(t('signed_in'))
        st.write(email)
        if st.button(t('sign_out'), use_container_width=True, key='yaffiliate_sign_out'):
            try:
                AuthService().sign_out()
            finally:
                for key in ('authenticated', 'auth_user_id', 'auth_user_email', 'supabase_access_token', 'supabase_refresh_token', 'loaded_campaign', 'loaded_campaign_id', 'generated_campaign', 'generated_campaign_id', 'quick_generated_campaign', 'quick_generated_zip', 'quick_generated_custom_product', 'quick_generated_campaign_id'):
                    st.session_state.pop(key, None)
                st.rerun()
