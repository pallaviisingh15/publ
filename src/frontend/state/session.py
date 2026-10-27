"""
Manages Streamlit session state and persists checkpoints to the filesystem
using the .rd.json convention defined in CLAUDE.md.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from backend.core.config import settings


def _checkpoint_path(session_id: str) -> Path:
    return Path(settings.session_dir) / "checkpoints" / f"{session_id}.rd.json"


def _snapshot_path(session_id: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(settings.session_dir) / "snapshots" / f"{session_id}_{ts}.rd.json"


def init_session() -> None:
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
        st.session_state["created_at"] = datetime.now(timezone.utc).isoformat()

    _restore_checkpoint(st.session_state["session_id"])


def save_checkpoint(data: dict) -> None:
    session_id: str = st.session_state["session_id"]
    payload = {
        "session_id": session_id,
        "created_at": st.session_state.get("created_at"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    path = _checkpoint_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def flush_snapshot(data: dict) -> None:
    session_id: str = st.session_state["session_id"]
    payload = {
        "session_id": session_id,
        "created_at": st.session_state.get("created_at"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    path = _snapshot_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _restore_checkpoint(session_id: str) -> None:
    path = _checkpoint_path(session_id)
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        for key, value in payload.get("data", {}).items():
            if key not in st.session_state:
                st.session_state[key] = value
