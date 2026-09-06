"""YAFFiliate workspace and subscription settings."""
from __future__ import annotations
from app.services.translation_service import ui
import os
import streamlit as st
from app.components.layout import page_header
from app.repositories.database import get_setting, upsert_setting
from app.services.stripe_service import StripeService
from app.services.subscription_service import SubscriptionService

def render() -> None:
    """Render workspace, subscription, and integration settings."""
    page_header('Workspace controls', 'Manage your YAffiliate workspace and subscription.', 'API keys and secrets remain securely stored outside the application.')
    st.subheader(ui('Workspace'))
    with st.form('settings'):
        name = st.text_input(ui('Workspace name'), get_setting('workspace_name', 'YAFFiliate Workspace'))
        currency_options = ['BRL', 'USD', 'EUR', 'GBP']
        saved_currency = get_setting('currency', 'BRL')
        currency_index = currency_options.index(saved_currency) if saved_currency in currency_options else 0
        currency = st.selectbox(ui('Default reporting currency'), currency_options, index=currency_index, help='This preference is for YAffiliate reporting. Stripe Checkout determines the supported local billing currency automatically.')
        budget = st.number_input(ui('Default monthly testing budget'), min_value=0.0, value=float(get_setting('monthly_budget', '1000')), step=100.0)
        ok = st.form_submit_button(ui('Save settings'))
    if ok:
        upsert_setting('workspace_name', name)
        upsert_setting('currency', currency)
        upsert_setting('monthly_budget', str(budget))
        st.success(ui('Settings saved.'))
    st.divider()
    st.subheader(ui('💳 YAffiliate Pro'))
    user_id = str(st.session_state.get('auth_user_id', '') or '').strip()
    email = str(st.session_state.get('auth_user_email', '') or '').strip()
    subscription = None
    subscription_error = None
    if user_id:
        try:
            subscription = SubscriptionService().get_subscription(user_id)
        except Exception as exc:
            subscription_error = str(exc)
    is_pro = bool(subscription and subscription.get('plan') == 'pro' and (subscription.get('status') in {'active', 'trialing'}))
    if is_pro:
        st.success(ui('Current plan: YAffiliate Pro'))
        st.caption(f"Subscription status: {subscription.get('status', 'active')}")
        if subscription.get('currency'):
            st.caption(f"Billing currency: {str(subscription['currency']).upper()}")
    else:
        st.write(ui('**Current plan:** Free'))
        st.info(ui('Your supported local subscription price and checkout language will be presented automatically by Stripe.'))
    if subscription_error:
        st.warning(f'The subscription database could not be checked. Details: {subscription_error}')
    if not is_pro:
        if st.button(ui('🚀 Upgrade to YAffiliate Pro'), type='primary', use_container_width=True):
            if not user_id or not email:
                st.error(ui('You must be signed in before starting a subscription.'))
            else:
                try:
                    checkout = StripeService().create_checkout_session(user_id=user_id, email=email)
                    checkout_url = checkout.get('url')
                    if checkout_url:
                        st.session_state['stripe_checkout_url'] = checkout_url
                    else:
                        st.error(ui('Stripe did not return a Checkout URL.'))
                except Exception as exc:
                    st.error(f'Unable to create checkout: {exc}')
        checkout_url = st.session_state.get('stripe_checkout_url')
        if checkout_url:
            st.link_button('Continue to secure payment →', checkout_url, use_container_width=True)
        st.caption(ui('Payments are processed securely by Stripe. YAFFiliate does not store your card details.'))
    else:
        st.session_state.pop('stripe_checkout_url', None)
    st.divider()
    st.subheader(ui('Integration status'))
    st.write(ui('OpenAI:'), '✅ Configured' if os.getenv('OPENAI_API_KEY') else '⚠️ Not configured')
    st.write(ui('Database:'), '✅ Connected')
    st.write(ui('Authentication:'), '✅ Active')
    stripe_key = os.getenv('STRIPE_SECRET_KEY', '').strip()
    if stripe_key.startswith('sk_live_'):
        stripe_status = '🟢 Live'
    elif stripe_key.startswith('sk_test_'):
        stripe_status = '✅ Sandbox'
    elif stripe_key:
        stripe_status = '⚠️ Invalid key'
    else:
        stripe_status = '⚠️ Not configured'
    st.write(ui('Stripe payments:'), stripe_status)
