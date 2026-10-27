"""
Customer Bills page.
Supports two search modes:
  (I)  Customer + optional Month/Year filter
  (II) Month & Year  (all customers)

Bill details and Generate Bills each open an @st.dialog modal.
Search results are held in st.session_state so they survive reruns
triggered by "View →" button clicks.
"""
import calendar
from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

from frontend.utils.api_client import api_get, api_post

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTH_MAP = {name: i + 1 for i, name in enumerate(MONTH_NAMES)}

# ── Dialogs (must be module-level for @st.dialog to work) ────────────────────

@st.dialog("Bill Details", width="large")
def _dialog_bill_details(bill: dict[str, Any]) -> None:
    cust_name = (bill.get("customer") or {}).get("name") or f"Customer #{bill['customer_id']}"
    month_label = date.fromisoformat(bill["month"]).strftime("%B %Y")

    st.markdown(
        f'<div class="dialog-header">'
        f"<strong>{cust_name}</strong> &nbsp;—&nbsp; {month_label}"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    try:
        items = api_get("/bill-items/", params={
            "customer_id": bill["customer_id"],
            "month": bill["month"],
        })
    except Exception as exc:
        st.error(f"Could not load bill items: {exc}")
        if st.button("Close"):
            st.rerun()
        return

    if not items:
        st.info("No itemised details found for this bill.")
    else:
        rows = []
        for item in items:
            pub = (item.get("publication") or {}).get("name") or f"Pub #{item['publication_id']}"
            rows.append({
                "Publication": pub,
                "Qty": item["quantity"],
                "Unit Price (₹)": f"{float(item['price']):,.2f}",
                "Discount (%)": f"{float(item['discount']):.1f}",
                "Amount (₹)": f"{float(item['amount']):,.2f}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        net = sum(float(i["amount"]) for i in items)
        _, col_net = st.columns([3, 1])
        col_net.metric("Net Amount Payable", f"₹ {net:,.2f}")

    st.markdown("")
    if st.button("✕  Close", use_container_width=False):
        st.rerun()


@st.dialog("Generate Bills", width="small")
def _dialog_generate_bills() -> None:
    st.markdown("**Select the billing period to generate:**")
    st.markdown("")

    cur_year = date.today().year
    col1, col2 = st.columns(2)
    month_name = col1.selectbox("Month", MONTH_NAMES,
                                index=date.today().month - 1)
    year = col2.selectbox("Year",
                          list(range(cur_year - 4, cur_year + 2)),
                          index=4)

    try:
        all_customers = api_get("/customers/")
    except Exception:
        all_customers = []
    cust_map: dict[str, int | None] = {"All Customers": None}
    cust_map.update({c["name"]: c["id"] for c in all_customers})
    cust_sel = st.selectbox("Generate For", list(cust_map.keys()))

    st.markdown("")
    if st.button("Generate Now", use_container_width=True, type="primary"):
        month_num = MONTH_MAP[month_name]
        last_day = calendar.monthrange(year, month_num)[1]
        with st.spinner("Generating bills…"):
            try:
                result = api_post("/bills/generate", json={
                    "start_date": f"{year}-{month_num:02d}-01",
                    "end_date":   f"{year}-{month_num:02d}-{last_day:02d}",
                    "customer_id": cust_map[cust_sel],
                })
                st.success(
                    f"✔ Generated: **{result['bills_created']}** new bill(s), "
                    f"**{result['bill_items_created']}** new item(s).  "
                    f"Updated: {result['bills_updated']} bill(s), "
                    f"{result['bill_items_updated']} item(s)."
                )
                # clear cached results so user sees fresh data next search
                st.session_state.pop("cb_results", None)
                st.session_state["cb_searched"] = False
            except Exception as exc:
                st.error(f"Generation failed: {exc}")


# ── Page ─────────────────────────────────────────────────────────────────────

def _init_state() -> None:
    for key, default in {
        "cb_search_mode": "Customer",
        "cb_cust_filter": "",
        "cb_results": None,
        "cb_searched": False,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default


def render() -> None:  # noqa: C901
    _init_state()

    # ── Page header ─────────────────────────────────────────────────────────
    hdr_col, btn_col = st.columns([5, 1])
    hdr_col.markdown(
        '<div class="page-header"><h2>Customer Bills</h2>'
        "<p>Search and view consolidated monthly bills</p></div>",
        unsafe_allow_html=True,
    )
    btn_col.markdown('<div style="margin-top:1.6rem;"></div>', unsafe_allow_html=True)
    if btn_col.button("📄 Generate Bills", use_container_width=True):
        _dialog_generate_bills()

    # ── Search controls ──────────────────────────────────────────────────────
    st.markdown("#### Search Bills")

    search_mode = st.radio(
        "Search By",
        ["Customer", "Month & Year"],
        horizontal=True,
        key="cb_search_mode",
    )

    try:
        all_customers = api_get("/customers/")
    except Exception as exc:
        st.error(f"Could not load customers: {exc}")
        all_customers = []

    cur_year = date.today().year
    year_opts_with_all = ["All"] + [str(y) for y in range(2020, cur_year + 2)]
    year_opts = [str(y) for y in range(2020, cur_year + 2)]

    selected_customer_id: int | None = None
    selected_month: int | None = None
    selected_year: int | None = None

    if search_mode == "Customer":
        st.markdown("**Customer**")
        c1, c2 = st.columns([2, 3])

        with c1:
            cust_filter = st.text_input(
                "🔍 Filter by name",
                placeholder="Type to narrow the list…",
                key="cb_cust_filter_input",
                label_visibility="collapsed",
            )
            st.caption("Type customer name above to filter")

        matching = [c for c in all_customers
                    if not cust_filter or cust_filter.lower() in c["name"].lower()]

        with c2:
            if matching:
                labels = ["— Select Customer —"] + [c["name"] for c in matching]
                choice = st.selectbox("Customer", labels, label_visibility="collapsed")
                if choice != "— Select Customer —":
                    selected_customer_id = next(
                        c["id"] for c in matching if c["name"] == choice
                    )
            elif cust_filter:
                st.warning("No customers match that name.")
            else:
                st.selectbox("Customer", ["— Select Customer —"],
                             label_visibility="collapsed")

        st.markdown("**Period (optional)**")
        p1, p2 = st.columns(2)
        month_sel = p1.selectbox("Month", ["All"] + MONTH_NAMES,
                                 key="cb_month_cust")
        year_sel  = p2.selectbox("Year",  year_opts_with_all,
                                 key="cb_year_cust")
        if month_sel != "All":
            selected_month = MONTH_MAP[month_sel]
        if year_sel != "All":
            selected_year = int(year_sel)

    else:  # Month & Year mode
        st.markdown("**Select Period**")
        p1, p2 = st.columns(2)
        month_sel = p1.selectbox("Month", MONTH_NAMES,
                                 index=date.today().month - 1,
                                 key="cb_month_my")
        year_sel  = p2.selectbox("Year",
                                 year_opts,
                                 index=max(0, len(year_opts) - 2),
                                 key="cb_year_my")
        selected_month = MONTH_MAP[month_sel]
        selected_year  = int(year_sel)

    # ── Action buttons ───────────────────────────────────────────────────────
    st.markdown("")
    sb1, sb2, _ = st.columns([1, 1, 5])
    search_clicked = sb1.button("🔍  Search", use_container_width=True, type="primary")
    if sb2.button("✕  Clear",  use_container_width=True):
        st.session_state["cb_results"]  = None
        st.session_state["cb_searched"] = False
        st.rerun()

    # ── Execute search ───────────────────────────────────────────────────────
    if search_clicked:
        if (search_mode == "Customer"
                and selected_customer_id is None
                and selected_month is None
                and selected_year is None):
            st.warning("Please select a customer or a period to search.")
        else:
            params: dict[str, Any] = {}
            if selected_customer_id:
                params["customer_id"] = selected_customer_id

            try:
                bills: list[dict] = api_get("/bills/", params=params)
            except Exception as exc:
                st.error(f"Search failed: {exc}")
                return

            if selected_month:
                bills = [b for b in bills
                         if date.fromisoformat(b["month"]).month == selected_month]
            if selected_year:
                bills = [b for b in bills
                         if date.fromisoformat(b["month"]).year == selected_year]

            st.session_state["cb_results"]  = bills
            st.session_state["cb_searched"] = True

    # ── Display results ──────────────────────────────────────────────────────
    if not st.session_state.get("cb_searched"):
        return

    st.divider()
    bills = st.session_state.get("cb_results") or []

    if not bills:
        st.info("No bills found for selected range.")
        return

    st.markdown(f"**{len(bills)} bill(s) found**")

    # Column headers
    h1, h2, h3, h4 = st.columns([2, 3, 2, 1])
    h1.markdown('<span class="tbl-hdr">Billing Month</span>', unsafe_allow_html=True)
    h2.markdown('<span class="tbl-hdr">Customer</span>',      unsafe_allow_html=True)
    h3.markdown('<span class="tbl-hdr">Total Amount</span>',  unsafe_allow_html=True)
    h4.markdown('<span class="tbl-hdr">Details</span>',       unsafe_allow_html=True)
    st.markdown('<hr class="tbl-divider">', unsafe_allow_html=True)

    for bill in bills:
        c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
        month_fmt  = date.fromisoformat(bill["month"]).strftime("%B %Y")
        cust_name  = (bill.get("customer") or {}).get("name") or f"#{bill['customer_id']}"
        amount_fmt = f"₹ {float(bill['total_amount']):,.2f}"

        c1.write(month_fmt)
        c2.write(cust_name)
        c3.write(amount_fmt)
        if c4.button("View →", key=f"view_bill_{bill['id']}",
                     help="View bill item details"):
            _dialog_bill_details(bill)
