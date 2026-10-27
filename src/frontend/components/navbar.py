"""Left-sidebar navigation for the dashboard."""
import streamlit as st

from frontend.utils.auth import logout

# (label, page_key, icon)
NAV_ITEMS = [
    ("Customer Bills",  "customer_bills",  "🧾"),
    ("Purchase Orders", "purchase_orders", "📋"),
    ("Publications",    "publications",    "📰"),
    ("Customers",       "customers",       "👥"),
]


def render_sidebar() -> str:
    """Render the sidebar and return the selected page key."""
    with st.sidebar:
        # ── Brand ────────────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center;padding:1.2rem 0 0.6rem;">
              <span style="font-size:2rem;">📰</span><br>
              <strong style="font-size:0.95rem;letter-spacing:1px;text-transform:uppercase;">
                News Distribution
              </strong><br>
              <span style="font-size:0.72rem;opacity:0.65;">Management System</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        # ── Navigation ───────────────────────────────────────────────────────
        labels = [f"{icon}  {label}" for label, _, icon in NAV_ITEMS]
        choice = st.radio(
            "Menu",
            labels,
            label_visibility="collapsed",
            key="sidebar_nav",
        )

        st.divider()

        # ── Signed-in user + Sign Out ────────────────────────────────────────
        username = st.session_state.get("username", "—")
        st.markdown(
            f'<div style="font-size:0.76rem;opacity:0.65;text-align:center;'
            f'margin-bottom:0.5rem;">Signed in as <strong>{username}</strong></div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign Out", use_container_width=True, key="btn_signout"):
            logout()
            st.rerun()

    # Map the chosen label back to a page key
    for label, key, icon in NAV_ITEMS:
        if choice == f"{icon}  {label}":
            return key
    return NAV_ITEMS[0][1]
