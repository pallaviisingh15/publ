from typing import Any

import httpx
import streamlit as st

BACKEND_URL = "http://localhost:8000"
_TIMEOUT = 10.0


def _headers() -> dict[str, str]:
    token = st.session_state.get("access_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _raise(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise RuntimeError(detail)


def api_get(path: str, params: dict | None = None) -> Any:
    resp = httpx.get(f"{BACKEND_URL}{path}", headers=_headers(), params=params, timeout=_TIMEOUT)
    _raise(resp)
    return resp.json()


def api_post(path: str, json: dict | None = None, data: dict | None = None) -> Any:
    resp = httpx.post(
        f"{BACKEND_URL}{path}", headers=_headers(), json=json, data=data, timeout=_TIMEOUT
    )
    _raise(resp)
    return resp.json()


def api_put(path: str, json: dict) -> Any:
    resp = httpx.put(f"{BACKEND_URL}{path}", headers=_headers(), json=json, timeout=_TIMEOUT)
    _raise(resp)
    return resp.json()


def api_delete(path: str) -> None:
    resp = httpx.delete(f"{BACKEND_URL}{path}", headers=_headers(), timeout=_TIMEOUT)
    _raise(resp)
