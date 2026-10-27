import pytest


@pytest.fixture()
def mock_session_state(monkeypatch):
    """Provides a dict-backed stand-in for st.session_state."""
    state: dict = {}
    monkeypatch.setattr("streamlit.session_state", state, raising=False)
    return state
