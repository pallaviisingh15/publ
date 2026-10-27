"""Customers — create, edit, delete, search."""
import pandas as pd
import streamlit as st

from frontend.utils.api_client import api_delete, api_get, api_post, api_put


# ── helpers ───────────────────────────────────────────────────────────────────

def _search_table(customers: list, search: str) -> None:
    filtered = customers
    if search:
        s = search.lower()
        filtered = [
            c for c in customers
            if s in c["name"].lower()
            or s in c["pin"].lower()
            or s in c["contact_number"].lower()
            or s in c["address"].lower()
        ]
    if filtered:
        rows = [
            {"ID": c["id"], "Name": c["name"],
             "Address": c["address"], "PIN": c["pin"], "Contact": c["contact_number"]}
            for c in filtered
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered)} of {len(customers)} customer(s) shown")
    else:
        msg = "No customers found." if not search else "No customers match the search term."
        st.info(msg)


def _tab_add() -> None:
    with st.form("form_add_cust"):
        c1, c2 = st.columns(2)
        name    = c1.text_input("Customer Name *")
        contact = c2.text_input("Contact Number *")
        pin     = c1.text_input("PIN Code *")
        address = st.text_area("Address *", height=80)
        if st.form_submit_button("Add Customer", use_container_width=True):
            if not all([name.strip(), contact.strip(), pin.strip(), address.strip()]):
                st.error("All fields are required.")
            else:
                try:
                    api_post("/customers/", json={
                        "name": name.strip(), "address": address.strip(),
                        "pin": pin.strip(), "contact_number": contact.strip(),
                    })
                    st.success(f"Customer '{name}' added.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))


def _tab_edit() -> None:
    cust_id = st.number_input("Customer ID to edit", min_value=1, step=1, key="edit_cust_id")
    if cust_id and st.button("Load Customer", key="load_cust"):
        try:
            st.session_state["cust_edit"] = api_get(f"/customers/{int(cust_id)}")
        except Exception as exc:
            st.error(str(exc))
            st.session_state.pop("cust_edit", None)

    c = st.session_state.get("cust_edit")
    if not c:
        return
    with st.form("form_edit_cust"):
        col1, col2 = st.columns(2)
        new_name    = col1.text_input("Name",    value=c["name"])
        new_contact = col2.text_input("Contact", value=c["contact_number"])
        new_pin     = col1.text_input("PIN",     value=c["pin"])
        new_address = st.text_area("Address",  value=c["address"], height=80)
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                api_put(f"/customers/{int(cust_id)}", json={
                    "name": new_name, "address": new_address,
                    "pin": new_pin, "contact_number": new_contact,
                })
                st.success("Customer updated.")
                st.session_state.pop("cust_edit", None)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))


def _tab_delete() -> None:
    del_id = st.number_input("Customer ID to delete", min_value=1, step=1, key="del_cust_id")
    if not del_id:
        return
    try:
        c = api_get(f"/customers/{int(del_id)}")
        st.warning(
            f"Delete customer **{c['name']}** "
            f"(PIN: {c['pin']}, Contact: {c['contact_number']}). "
            "Associated orders and bills will become orphaned. This cannot be undone."
        )
        if st.button("Confirm Delete", key="confirm_del_cust", type="primary"):
            api_delete(f"/customers/{int(del_id)}")
            st.success(f"Customer '{c['name']}' deleted.")
            st.rerun()
    except Exception:
        st.info("Enter a valid Customer ID to load details.")


# ── page entry ────────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(
        '<div class="page-header"><h2>Customers</h2>'
        "<p>Manage delivery subscribers</p></div>",
        unsafe_allow_html=True,
    )
    try:
        customers = api_get("/customers/")
    except Exception as exc:
        st.error(f"Could not load customers: {exc}")
        return

    search = st.text_input(
        "🔍 Search customers",
        placeholder="Filter by name, PIN code, or contact number…",
        key="cust_search",
    )
    _search_table(customers, search)
    st.divider()

    tab_add, tab_edit, tab_del = st.tabs(
        ["➕  Add New Customer", "✏️  Edit Customer", "🗑️  Delete Customer"]
    )
    with tab_add:
        _tab_add()
    with tab_edit:
        _tab_edit()
    with tab_del:
        _tab_delete()
