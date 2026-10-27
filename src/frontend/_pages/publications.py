"""Publications — create, edit, delete, search."""
import pandas as pd
import streamlit as st

from frontend.utils.api_client import api_delete, api_get, api_post, api_put

FREQ_OPTIONS = ["daily", "weekly", "monthly", "quarterly", "bi_annual", "annual"]
FREQ_LABELS  = {
    "daily": "Daily", "weekly": "Weekly", "monthly": "Monthly",
    "quarterly": "Quarterly", "bi_annual": "Bi-Annual", "annual": "Annual",
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _search_table(pubs: list, search: str) -> None:
    filtered = pubs
    if search:
        s = search.lower()
        filtered = [p for p in pubs
                    if s in p["name"].lower() or s in p["frequency"].lower()]
    if filtered:
        rows = [
            {
                "ID":                 p["id"],
                "Name":               p["name"],
                "Frequency":          FREQ_LABELS.get(p["frequency"], p["frequency"]),
                "Base Price (₹)":     float(p["base_price"]),
                "Purchase Price (₹)": float(p["purchase_price"]),
            }
            for p in filtered
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered)} of {len(pubs)} publication(s) shown")
    else:
        msg = "No publications found." if not search else "No publications match the search term."
        st.info(msg)


def _tab_add() -> None:
    with st.form("form_add_pub"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Publication Name *")
        freq = c2.selectbox("Frequency *", FREQ_OPTIONS,
                            format_func=lambda k: FREQ_LABELS[k])
        base = c1.number_input("Base Price (₹) *", min_value=0.0, step=0.5, format="%.2f")
        pp   = c2.number_input("Purchase Price (₹) *", min_value=0.0, step=0.5, format="%.2f")
        if st.form_submit_button("Add Publication", use_container_width=True):
            if not name.strip():
                st.error("Publication name is required.")
            else:
                try:
                    api_post("/publications/", json={
                        "name": name.strip(), "frequency": freq,
                        "base_price": base, "purchase_price": pp,
                    })
                    st.success(f"Publication '{name}' added.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))


def _tab_edit() -> None:
    pub_id = st.number_input("Publication ID to edit", min_value=1, step=1, key="edit_pub_id")
    if pub_id and st.button("Load Publication", key="load_pub"):
        try:
            st.session_state["pub_edit"] = api_get(f"/publications/{int(pub_id)}")
        except Exception as exc:
            st.error(str(exc))
            st.session_state.pop("pub_edit", None)

    p = st.session_state.get("pub_edit")
    if not p:
        return
    with st.form("form_edit_pub"):
        c1, c2 = st.columns(2)
        new_name = c1.text_input("Name", value=p["name"])
        new_freq = c2.selectbox("Frequency", FREQ_OPTIONS,
                                index=FREQ_OPTIONS.index(p["frequency"]),
                                format_func=lambda k: FREQ_LABELS[k])
        new_base = c1.number_input("Base Price (₹)", value=float(p["base_price"]),
                                   min_value=0.0, step=0.5, format="%.2f")
        new_pp   = c2.number_input("Purchase Price (₹)", value=float(p["purchase_price"]),
                                   min_value=0.0, step=0.5, format="%.2f")
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                api_put(f"/publications/{int(pub_id)}", json={
                    "name": new_name, "frequency": new_freq,
                    "base_price": new_base, "purchase_price": new_pp,
                })
                st.success("Publication updated.")
                st.session_state.pop("pub_edit", None)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))


def _tab_delete() -> None:
    del_id = st.number_input("Publication ID to delete", min_value=1, step=1, key="del_pub_id")
    if not del_id:
        return
    try:
        p = api_get(f"/publications/{int(del_id)}")
        st.warning(
            f"Delete **{p['name']}** ({FREQ_LABELS.get(p['frequency'], p['frequency'])}). "
            "This cannot be undone."
        )
        if st.button("Confirm Delete", key="confirm_del_pub", type="primary"):
            api_delete(f"/publications/{int(del_id)}")
            st.success(f"Publication '{p['name']}' deleted.")
            st.rerun()
    except Exception:
        st.info("Enter a valid Publication ID to load details.")


# ── page entry ────────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(
        '<div class="page-header"><h2>Publications</h2>'
        "<p>Manage newspaper and magazine titles</p></div>",
        unsafe_allow_html=True,
    )
    try:
        pubs = api_get("/publications/")
    except Exception as exc:
        st.error(f"Could not load publications: {exc}")
        return

    search = st.text_input(
        "🔍 Search publications",
        placeholder="Filter by name or frequency (e.g. daily, weekly)…",
        key="pub_search",
    )
    _search_table(pubs, search)
    st.divider()

    tab_add, tab_edit, tab_del = st.tabs(
        ["➕  Add New Publication", "✏️  Edit Publication", "🗑️  Delete Publication"]
    )
    with tab_add:
        _tab_add()
    with tab_edit:
        _tab_edit()
    with tab_del:
        _tab_delete()
