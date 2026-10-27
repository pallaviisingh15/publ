"""Login page with client-side validation before hitting the API."""
import streamlit as st

from frontend.utils.auth import login


def render() -> None:
    # Centre the card with columns
    _, card_col, _ = st.columns([1, 2, 1])

    with card_col:
        st.markdown(
            """
            <div class="login-card">
              <div class="login-logo">
                <span style="font-size:2.8rem;">📰</span>
                <h2>Newspaper Distribution</h2>
                <p>Management System</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                autocomplete="username",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                autocomplete="current-password",
            )
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            # ── Client-side validation ─────────────────────────────────────
            errors: list[str] = []
            if not username.strip():
                errors.append("Username is required.")
            if not password:
                errors.append("Password is required.")

            if errors:
                for msg in errors:
                    st.error(msg)
            else:
                with st.spinner("Verifying credentials…"):
                    success = login(username.strip(), password)

                if success:
                    st.success("Login successful. Loading dashboard…")
                    st.rerun()
                else:
                    err = st.session_state.pop("login_error", "Invalid username or password.")
                    st.error(err)
