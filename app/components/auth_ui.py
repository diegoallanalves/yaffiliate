"""YAFFiliate authentication UI — premium landing page."""

from __future__ import annotations

import logging
import streamlit as st

from app.services.auth_service import AuthService
from app.services.growth_analytics_service import GrowthAnalyticsService
from app.services.persistent_session_service import PersistentSessionService
from app.services.translation_service import get_language, t, ui

logger = logging.getLogger(__name__)
PENDING_KEY = "_persistent_login_pending"

AUTH_CSS = """
<style>
/* Applied only when the authentication page renders. */
/* Full-screen auth experience: no Streamlit navigation chrome. */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {display:none !important;}
[data-testid="stAppViewContainer"] {
  margin-left:0 !important;
  width:100% !important;
}
[data-testid="stMain"] {width:100% !important;}
[data-testid="stMainBlockContainer"] {
  max-width:none !important;
  width:100% !important;
  padding:0 !important;
}
[data-testid="stHorizontalBlock"]:has(.ya-art-anchor) > div {
  min-width:0 !important;
}

.stApp {background:#050509;color:#f6f5ff;}
[data-testid="stHeader"] {background:transparent;}
.block-container {
  max-width:100vw !important;
  width:100% !important;
  padding:0 !important;
  margin:0 !important;
}
[data-testid="stHorizontalBlock"]:has(.ya-art-anchor) {
  gap:0 !important;
  column-gap:0 !important;
  min-height:100vh;
  border:0;
  border-radius:0;
  overflow:hidden;
  box-shadow:none;
}
[data-testid="stColumn"]:has(.ya-art-anchor) {
  background:
    url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20700%20800%22%3E%3Cg%20fill%3D%22none%22%20stroke%3D%22%23d6a6ff%22%20stroke-opacity%3D%22.37%22%20stroke-width%3D%22.8%22%3E%3Cpath%20d%3D%22M%20-80%20350%20Q%20210%2070%20440%20370%20T%20790%20230%22%2F%3E%3Cpath%20d%3D%22M%20-80%20358%20Q%20210%2073%20440%20372%20T%20790%20236%22%2F%3E%3Cpath%20d%3D%22M%20-80%20366%20Q%20210%2076%20440%20374%20T%20790%20242%22%2F%3E%3Cpath%20d%3D%22M%20-80%20374%20Q%20210%2079%20440%20376%20T%20790%20248%22%2F%3E%3Cpath%20d%3D%22M%20-80%20382%20Q%20210%2082%20440%20378%20T%20790%20254%22%2F%3E%3Cpath%20d%3D%22M%20-80%20390%20Q%20210%2085%20440%20380%20T%20790%20260%22%2F%3E%3Cpath%20d%3D%22M%20-80%20398%20Q%20210%2088%20440%20382%20T%20790%20266%22%2F%3E%3Cpath%20d%3D%22M%20-80%20406%20Q%20210%2091%20440%20384%20T%20790%20272%22%2F%3E%3Cpath%20d%3D%22M%20-80%20414%20Q%20210%2094%20440%20386%20T%20790%20278%22%2F%3E%3Cpath%20d%3D%22M%20-80%20422%20Q%20210%2097%20440%20388%20T%20790%20284%22%2F%3E%3Cpath%20d%3D%22M%20-80%20430%20Q%20210%20100%20440%20390%20T%20790%20290%22%2F%3E%3Cpath%20d%3D%22M%20-80%20438%20Q%20210%20103%20440%20392%20T%20790%20296%22%2F%3E%3Cpath%20d%3D%22M%20-80%20446%20Q%20210%20106%20440%20394%20T%20790%20302%22%2F%3E%3Cpath%20d%3D%22M%20-80%20454%20Q%20210%20109%20440%20396%20T%20790%20308%22%2F%3E%3Cpath%20d%3D%22M%20-80%20462%20Q%20210%20112%20440%20398%20T%20790%20314%22%2F%3E%3Cpath%20d%3D%22M%20-80%20470%20Q%20210%20115%20440%20400%20T%20790%20320%22%2F%3E%3Cpath%20d%3D%22M%20-80%20478%20Q%20210%20118%20440%20402%20T%20790%20326%22%2F%3E%3Cpath%20d%3D%22M%20-80%20486%20Q%20210%20121%20440%20404%20T%20790%20332%22%2F%3E%3Cpath%20d%3D%22M%20-80%20494%20Q%20210%20124%20440%20406%20T%20790%20338%22%2F%3E%3Cpath%20d%3D%22M%20-80%20502%20Q%20210%20127%20440%20408%20T%20790%20344%22%2F%3E%3Cpath%20d%3D%22M%20-80%20510%20Q%20210%20130%20440%20410%20T%20790%20350%22%2F%3E%3Cpath%20d%3D%22M%20-80%20518%20Q%20210%20133%20440%20412%20T%20790%20356%22%2F%3E%3Cpath%20d%3D%22M%20-80%20526%20Q%20210%20136%20440%20414%20T%20790%20362%22%2F%3E%3Cpath%20d%3D%22M%20-80%20534%20Q%20210%20139%20440%20416%20T%20790%20368%22%2F%3E%3Cpath%20d%3D%22M%20-80%20542%20Q%20210%20142%20440%20418%20T%20790%20374%22%2F%3E%3Cpath%20d%3D%22M%20-80%20550%20Q%20210%20145%20440%20420%20T%20790%20380%22%2F%3E%3Cpath%20d%3D%22M%20-80%20558%20Q%20210%20148%20440%20422%20T%20790%20386%22%2F%3E%3Cpath%20d%3D%22M%20-80%20566%20Q%20210%20151%20440%20424%20T%20790%20392%22%2F%3E%3Cpath%20d%3D%22M%20-80%20574%20Q%20210%20154%20440%20426%20T%20790%20398%22%2F%3E%3Cpath%20d%3D%22M%20-80%20582%20Q%20210%20157%20440%20428%20T%20790%20404%22%2F%3E%3Cpath%20d%3D%22M%20-80%20590%20Q%20210%20160%20440%20430%20T%20790%20410%22%2F%3E%3Cpath%20d%3D%22M%20-80%20598%20Q%20210%20163%20440%20432%20T%20790%20416%22%2F%3E%3Cpath%20d%3D%22M%20-80%20606%20Q%20210%20166%20440%20434%20T%20790%20422%22%2F%3E%3Cpath%20d%3D%22M%20-80%20614%20Q%20210%20169%20440%20436%20T%20790%20428%22%2F%3E%3Cpath%20d%3D%22M%20-80%20622%20Q%20210%20172%20440%20438%20T%20790%20434%22%2F%3E%3Cpath%20d%3D%22M%20-80%20630%20Q%20210%20175%20440%20440%20T%20790%20440%22%2F%3E%3Cpath%20d%3D%22M%20-80%20638%20Q%20210%20178%20440%20442%20T%20790%20446%22%2F%3E%3Cpath%20d%3D%22M%20-80%20646%20Q%20210%20181%20440%20444%20T%20790%20452%22%2F%3E%3Cpath%20d%3D%22M%20-80%20654%20Q%20210%20184%20440%20446%20T%20790%20458%22%2F%3E%3Cpath%20d%3D%22M%20-80%20662%20Q%20210%20187%20440%20448%20T%20790%20464%22%2F%3E%3Cpath%20d%3D%22M%20-80%20670%20Q%20210%20190%20440%20450%20T%20790%20470%22%2F%3E%3Cpath%20d%3D%22M%20-80%20678%20Q%20210%20193%20440%20452%20T%20790%20476%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E") center 60% / 110% auto no-repeat,
    radial-gradient(ellipse at 70% 14%,#4bd4d1 0%,transparent 42%),
    radial-gradient(ellipse at 9% 65%,#8618df 0%,transparent 64%),
    linear-gradient(145deg,#173a98,#7312d6 52%,#24065d);
  padding:30px 34px !important;
  min-height:100vh;
}
[data-testid="stColumn"]:has(.ya-form-anchor) {
  background:#08080b;
  padding:clamp(100px,18vh,220px) clamp(30px,7vw,140px) 42px !important;
  min-height:100vh;
}
.ya-art-anchor {height:1px;}
.ya-logo {font-weight:800;color:#fff;font-size:18px;letter-spacing:-.5px;}
.ya-logo span {color:#9aeaff;}
.ya-art-copy {margin-top:clamp(340px,55vh,660px);color:#fff;}
.ya-art-copy h2 {font-size:33px;line-height:1.1;font-weight:750;}
.ya-art-copy p {font-size:15px;max-width:340px;color:#e7ddff;}
.ya-form-anchor {height:1px;}
.ya-form-heading {font-size:28px;font-weight:750;color:#fff;margin:0 0 8px;}
.ya-form-sub {color:#aaa5b6;font-size:14px;margin-bottom:22px;}
div[data-testid="stForm"] {background:transparent;border:0;padding:0;}
.stTabs [data-baseweb="tab-list"] {gap:14px;background:transparent;}
.stTabs [data-baseweb="tab"] {font-size:14px;color:#c5bdd3;}
.stTabs [aria-selected="true"] {color:#fff;}
.stTabs [data-baseweb="tab-highlight"] {background:#ab44f5;}
.stTextInput label {font-size:14px !important;color:#e7e2ed !important;}
.stTextInput input {
  min-height:46px !important;background:#101014 !important;
  border:1px solid #484050 !important;border-radius:4px !important;
  color:white !important;
}
.stFormSubmitButton button[kind="primary"] {
  background:#0b090f !important;border:1px solid #aa45ed !important;
  border-radius:4px !important;color:#fff !important;
  min-height:44px;font-weight:650;
}
.stFormSubmitButton button[kind="primary"]:hover {
  background:#3a1558 !important;border-color:#d18cff !important;
}
.ya-footer {font-size:12px;color:#8e8898;text-align:center;margin-top:26px;}
@media(max-width:760px) {
  .block-container {padding:0 !important;}
  [data-testid="stHorizontalBlock"]:has(.ya-art-anchor) {min-height:100vh;}
  [data-testid="stColumn"]:has(.ya-art-anchor) {
    min-height:32vh;padding:20px !important;
  }
  .ya-art-copy {margin-top:85px;}
  .ya-art-copy h2 {font-size:23px;}
  [data-testid="stColumn"]:has(.ya-form-anchor) {
    min-height:68vh;padding:40px 24px 50px !important;
  }
}
</style>
"""


def _store_auth_session(response) -> bool:
    """Store the authenticated Supabase session in Streamlit."""
    user = getattr(response, "user", None)
    session = getattr(response, "session", None)
    if user is None or session is None:
        return False
    access_token = getattr(session, "access_token", None)
    refresh_token = getattr(session, "refresh_token", None)
    user_id = getattr(user, "id", None)
    if not access_token or not refresh_token or not user_id:
        return False
    st.session_state["auth_user_id"] = str(user_id)
    st.session_state["auth_user_email"] = str(
        getattr(user, "email", "") or ""
    )
    st.session_state["supabase_access_token"] = str(access_token)
    st.session_state["supabase_refresh_token"] = str(refresh_token)
    st.session_state["authenticated"] = True
    return True


def _queue_persistent_session() -> None:
    st.session_state[PENDING_KEY] = True


def _finish_persistent_session() -> None:
    if not st.session_state.get(PENDING_KEY):
        return
    user_id = st.session_state.get("auth_user_id")
    refresh_token = st.session_state.get("supabase_refresh_token")
    if not user_id or not refresh_token:
        st.session_state.pop(PENDING_KEY, None)
        return
    try:
        PersistentSessionService().create(
            user_id=str(user_id),
            refresh_token=str(refresh_token),
        )
    except Exception:
        logger.exception("Could not create persistent login session.")
        return
    st.session_state.pop(PENDING_KEY, None)
    st.rerun()


def render_auth_page() -> None:
    """Render the split-screen YAffiliate login experience."""
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    left, right = st.columns(
        [1, 1],
        gap="small",
        vertical_alignment="top",
    )

    with left:
        st.markdown(
            '<div class="ya-art-anchor"></div>'
            '<div class="ya-logo">✦ Y<span>Affiliate</span></div>'
            '<div class="ya-art-copy">'
            '<h2>Smarter affiliate marketing.</h2>'
            '<p>Create campaigns, explore products, '
            'and grow with AI-powered tools.</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="ya-form-anchor"></div>'
            '<div class="ya-form-heading">Sign in to your account</div>'
            '<div class="ya-form-sub">'
            'Welcome back to YAffiliate.'
            '</div>',
            unsafe_allow_html=True,
        )

        auth = AuthService()
        sign_in, sign_up = st.tabs(
            [ui("Sign In"), ui("Create Account")]
        )

        with sign_in:
            _sign_in(auth)

        with sign_up:
            _sign_up(auth)

        st.markdown(
            '<div class="ya-footer">'
            'Secure account access powered by Supabase'
            '</div>',
            unsafe_allow_html=True,
        )


def _sign_in(auth: AuthService) -> None:
    with st.form("auth_sign_in"):
        email = st.text_input(
            ui("Email"), key="signin_email",
            placeholder="you@example.com",
        )
        password = st.text_input(
            ui("Password"), type="password",
            key="signin_password", placeholder="Your password",
        )
        submitted = st.form_submit_button(
            ui("Sign In"), type="primary",
            use_container_width=True,
        )
    if not submitted:
        return
    try:
        response = auth.sign_in(email, password)
        if not _store_auth_session(response):
            st.error(ui("Sign in did not return an authenticated session."))
            return
        _queue_persistent_session()
        st.rerun()
    except Exception:
        logger.exception("Sign in failed.")
        st.error(ui("Sign in failed. Please check your credentials."))


def _sign_up(auth: AuthService) -> None:
    with st.form("auth_sign_up"):
        email = st.text_input(
            ui("Email"), key="signup_email",
            placeholder="you@example.com",
        )
        password = st.text_input(
            ui("Password"), type="password",
            key="signup_password",
        )
        confirm = st.text_input(
            ui("Confirm password"), type="password",
            key="signup_confirm",
        )
        submitted = st.form_submit_button(
            ui("Create Account"), type="primary",
            use_container_width=True,
        )
    if not submitted:
        return
    if password != confirm:
        st.error(ui("Passwords do not match."))
        return
    if len(password) < 8:
        st.error(ui("Password must contain at least 8 characters."))
        return
    try:
        response = auth.sign_up(email, password, get_language())
        user = getattr(response, "user", None)
        session = getattr(response, "session", None)
        if user is None:
            st.error(ui("Account could not be created."))
            return
        try:
            GrowthAnalyticsService().track(
                "signup",
                event_page="auth",
                user_id=str(user.id),
                metadata={
                    "language": get_language(),
                    "email_confirmation_required": session is None,
                },
            )
        except Exception:
            logger.exception("Signup analytics tracking failed.")
        if session is None:
            st.success(ui(
                "Account created. Check your email, "
                "confirm your address, then return and sign in."
            ))
            return
        if not _store_auth_session(response):
            st.error(ui(
                "Account was created but the authenticated "
                "session could not be stored. Please sign in."
            ))
            return
        _queue_persistent_session()
        st.rerun()
    except Exception:
        logger.exception("Account creation failed.")
        st.error(ui("Account creation failed. Please try again."))


def _persistent_cookie_writer() -> None:
    if st.session_state.get(PENDING_KEY):
        _finish_persistent_session()


def render_user_sidebar() -> None:
    _persistent_cookie_writer()
    email = st.session_state.get(
        "auth_user_email", "Signed-in user"
    )
    with st.sidebar:
        st.divider()
        st.caption(t("signed_in"))
        st.write(email)
        if st.button(
            t("sign_out"),
            use_container_width=True,
            key="yaffiliate_sign_out",
        ):
            try:
                PersistentSessionService().revoke_current()
            except Exception:
                logger.exception("Persistent session revocation failed.")
            try:
                AuthService().sign_out()
            except Exception:
                logger.exception("Supabase sign out failed.")
            finally:
                for key in (
                    PENDING_KEY,
                    "authenticated",
                    "auth_user_id",
                    "auth_user_email",
                    "supabase_access_token",
                    "supabase_refresh_token",
                    "loaded_campaign",
                    "loaded_campaign_id",
                    "generated_campaign",
                    "generated_campaign_id",
                    "quick_generated_campaign",
                    "quick_generated_zip",
                    "quick_generated_custom_product",
                    "quick_generated_campaign_id",
                ):
                    st.session_state.pop(key, None)
                st.rerun()


