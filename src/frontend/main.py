"""Application entry point — login gate + dashboard routing."""
from pathlib import Path

import streamlit as st

# ── Page config (must be the very first Streamlit call) ───────────────────────
st.set_page_config(
    page_title="Newspaper Distribution System",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
_css = Path(__file__).parent / "assets" / "style.css"
if _css.exists():
    st.markdown(f"<style>{_css.read_text()}</style>", unsafe_allow_html=True)

# ── Imports after page config ─────────────────────────────────────────────────
# _pages/ uses an underscore prefix so Streamlit does NOT auto-discover these
# files as additional navigation entries in the sidebar.
from frontend.components.navbar import render_sidebar  # noqa: E402
from frontend._pages import (  # noqa: E402
    login,
    customer_bills,
    purchase_orders,
    publications,
    customers,
)
from frontend.utils.auth import is_authenticated  # noqa: E402

# ── Session defaults ──────────────────────────────────────────────────────────
st.session_state.setdefault("access_token", "")
st.session_state.setdefault("logged_in", False)

# ── Routing ───────────────────────────────────────────────────────────────────
if not is_authenticated():
    login.render()
else:
    page_key = render_sidebar()

    _PAGES = {
        "customer_bills":  customer_bills.render,
        "purchase_orders": purchase_orders.render,
        "publications":    publications.render,
        "customers":       customers.render,
    }

    renderer = _PAGES.get(page_key, customer_bills.render)
    try:
        renderer()
    except Exception as exc:
        st.error(f"Page error: {exc}")
        st.exception(exc)
