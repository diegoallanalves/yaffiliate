"""First-party browser cookie bridge for Streamlit Components V2 (1.60+)."""
from __future__ import annotations

import streamlit as st

COOKIE_NAME = "yaffiliate_session"
COOKIE_STATE = "_yaffiliate_browser_cookie"
COOKIE_READY = "_yaffiliate_browser_ready"
COOKIE_COMMAND = "_yaffiliate_cookie_command"
COOKIE_ACK = "_yaffiliate_cookie_ack"

# Components V2 execute in the application document, not a third-party iframe.
_JS = r"""
export default function({data, setStateValue}) {
  const name = 'yaffiliate_session';
  const read = () => {
    const prefix = name + '=';
    const part = document.cookie.split('; ').find(x => x.startsWith(prefix));
    return part ? decodeURIComponent(part.slice(prefix.length)) : '';
  };
  const cmd = data?.command;
  try {
    if (cmd && cmd.id && cmd.id !== window.__yaffiliateLastCookieCmd) {
      if (cmd.action === 'set' && cmd.token) {
        document.cookie = name + '=' + encodeURIComponent(cmd.token)
          + '; Path=/; Max-Age=2592000; SameSite=Lax'
          + (location.protocol === 'https:' ? '; Secure' : '');
      } else if (cmd.action === 'delete') {
        document.cookie = name + '=; Path=/; Max-Age=0; SameSite=Lax'
          + (location.protocol === 'https:' ? '; Secure' : '');
      }
      // Acknowledge only after the browser reflects the requested state.
      const actual = read();
      const success = cmd.action === 'delete' ? !actual : actual === cmd.token;
      if (success) {
        window.__yaffiliateLastCookieCmd = cmd.id;
        setStateValue('ack', cmd.id);
      }
    }
    setStateValue('cookie', read());
    setStateValue('ready', true);
  } catch (err) {
    console.error('YAFFiliate browser cookie error', err);
    setStateValue('ready', false);
  }
}
"""

_bridge = st.components.v2.component(
    "yaffiliate_first_party_cookie_bridge", js=_JS
)


def mount_browser_cookie() -> None:
    """Mount once on every app execution, before session restoration."""
    command = st.session_state.get(COOKIE_COMMAND)
    result = _bridge(
        key="yaffiliate_browser_cookie_bridge",
        data={"command": command},
        on_cookie_change=lambda: None,
        on_ready_change=lambda: None,
        on_ack_change=lambda: None,
    )
    st.session_state[COOKIE_READY] = bool(getattr(result, "ready", False))
    cookie = getattr(result, "cookie", None)
    if cookie is not None:
        st.session_state[COOKIE_STATE] = str(cookie)
    ack = getattr(result, "ack", None)
    if command and ack == command.get("id"):
        st.session_state[COOKIE_ACK] = ack
        st.session_state.pop(COOKIE_COMMAND, None)


def queue_cookie(token: str | None) -> None:
    """Queue a write/delete for the next Streamlit render."""
    import secrets
    st.session_state[COOKIE_COMMAND] = {
        "id": secrets.token_hex(12),
        "action": "set" if token else "delete",
        "token": token or "",
    }
    st.session_state.pop(COOKIE_ACK, None)
