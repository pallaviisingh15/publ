"""Purchase Orders — create, edit, delete, search."""
from datetime import date

import pandas as pd
import streamlit as st

from frontend.utils.api_client import api_delete, api_get, api_post, api_put

_PLACEHOLDER = "— Select —"
_LBL_PRICE   = "Sale Price (₹)"
_LBL_DISC    = "Discount (%)"


# ── helpers ───────────────────────────────────────────────────────────────────

def _cust_map(customers: list) -> dict[str, int]:
    return {f"{c['name']} (#{c['id']})": c["id"] for c in customers}


def _pub_map(publications: list) -> dict[str, dict]:
    return {f"{p['name']} (#{p['id']})": p for p in publications}


def _search_table(orders: list, search: str) -> None:
    filtered = orders
    if search:
        s = search.lower()
        filtered = [
            o for o in orders
            if s in (o.get("customer") or {}).get("name", "").lower()
            or s in (o.get("publication") or {}).get("name", "").lower()
            or s in (o.get("purchase_date") or "")
        ]
    if filtered:
        rows = [
            {
                "ID":             o["id"],
                "Date":           o["purchase_date"],
                "Customer":       (o.get("customer") or {}).get("name", o["customer_id"]),
                "Publication":    (o.get("publication") or {}).get("name", o["publication_id"]),
                _LBL_PRICE:      float(o["sale_price"]),
                _LBL_DISC:       float(o["discount"]),
            }
            for o in filtered
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption(f"{len(filtered)} of {len(orders)} order(s) shown")
    else:
        msg = "No purchase orders found." if not search else "No orders match the search term."
        st.info(msg)


def _tab_add(cust_map: dict, pub_map: dict) -> None:
    with st.form("form_add_po"):
        c1, c2 = st.columns(2)
        cust_label = c1.selectbox("Customer *",   [_PLACEHOLDER] + list(cust_map))
        pub_label  = c2.selectbox("Publication *",[_PLACEHOLDER] + list(pub_map))
        po_date    = c1.date_input("Purchase Date *", value=date.today())
        default_price = float(pub_map[pub_label]["base_price"]) if pub_label in pub_map else 0.0
        sale_price = c2.number_input(_LBL_PRICE, value=default_price,
                                     min_value=0.0, step=0.5, format="%.2f")
        discount   = st.number_input(_LBL_DISC, value=0.0,
                                     min_value=0.0, max_value=100.0,
                                     step=0.5, format="%.2f")
        if st.form_submit_button("Add Order", use_container_width=True):
            if cust_label == _PLACEHOLDER or pub_label == _PLACEHOLDER:
                st.error("Customer and Publication are required.")
            else:
                try:
                    api_post("/purchase-orders/", json={
                        "purchase_date":  str(po_date),
                        "customer_id":    cust_map[cust_label],
                        "publication_id": pub_map[pub_label]["id"],
                        "sale_price":     sale_price,
                        "discount":       discount,
                    })
                    st.success("Purchase order added.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))


def _tab_edit() -> None:
    order_id = st.number_input("Order ID to edit", min_value=1, step=1, key="edit_po_id")
    if order_id and st.button("Load Order", key="load_po"):
        try:
            st.session_state["po_edit"] = api_get(f"/purchase-orders/{int(order_id)}")
        except Exception as exc:
            st.error(str(exc))
            st.session_state.pop("po_edit", None)

    o = st.session_state.get("po_edit")
    if not o:
        return
    with st.form("form_edit_po"):
        c1, c2 = st.columns(2)
        new_date  = c1.date_input("Purchase Date",
                                  value=date.fromisoformat(o["purchase_date"]))
        new_price = c2.number_input(_LBL_PRICE, value=float(o["sale_price"]),
                                    min_value=0.0, step=0.5, format="%.2f")
        new_disc  = st.number_input(_LBL_DISC, value=float(o["discount"]),
                                    min_value=0.0, max_value=100.0,
                                    step=0.5, format="%.2f")
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                api_put(f"/purchase-orders/{int(order_id)}", json={
                    "purchase_date": str(new_date),
                    "sale_price":    new_price,
                    "discount":      new_disc,
                })
                st.success("Order updated.")
                st.session_state.pop("po_edit", None)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))


def _tab_delete() -> None:
    del_id = st.number_input("Order ID to delete", min_value=1, step=1, key="del_po_id")
    if not del_id:
        return
    try:
        o    = api_get(f"/purchase-orders/{int(del_id)}")
        cust = (o.get("customer") or {}).get("name", "—")
        pub  = (o.get("publication") or {}).get("name", "—")
        st.warning(
            f"Delete order **#{del_id}**: customer **{cust}**, "
            f"publication **{pub}**, dated **{o['purchase_date']}**. "
            "This cannot be undone."
        )
        if st.button("Confirm Delete", key="confirm_del_po", type="primary"):
            api_delete(f"/purchase-orders/{int(del_id)}")
            st.success(f"Order #{del_id} deleted.")
            st.rerun()
    except Exception:
        st.info("Enter a valid Order ID to load order details.")


# ── page entry ────────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(
        '<div class="page-header"><h2>Purchase Orders</h2>'
        "<p>Manage customer publication subscriptions</p></div>",
        unsafe_allow_html=True,
    )
    try:
        orders       = api_get("/purchase-orders/")
        customers    = api_get("/customers/")
        publications = api_get("/publications/")
    except Exception as exc:
        st.error(f"Could not load data: {exc}")
        return

    search = st.text_input(
        "🔍 Search orders",
        placeholder="Filter by customer, publication, or date (YYYY-MM-DD)…",
        key="po_search",
    )
    _search_table(orders, search)
    st.divider()

    cm = _cust_map(customers)
    pm = _pub_map(publications)

    tab_add, tab_edit, tab_del = st.tabs(
        ["➕  Add New Order", "✏️  Edit Order", "🗑️  Delete Order"]
    )
    with tab_add:
        _tab_add(cm, pm)
    with tab_edit:
        _tab_edit()
    with tab_del:
        _tab_delete()
