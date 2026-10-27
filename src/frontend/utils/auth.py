import streamlit as st
from frontend.utils.api_client import api_post


def login(username: str, password: str) -> bool:
    try:
        result = api_post(
            "/auth/login",
            data={"username": username, "password": password},
        )
        st.session_state["access_token"] = result["access_token"]
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        return True
    except Exception as e:
        st.session_state["login_error"] = str(e)
        return False


def logout() -> None:
    for key in ("access_token", "logged_in", "username"):
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return bool(st.session_state.get("logged_in") and st.session_state.get("access_token"))
