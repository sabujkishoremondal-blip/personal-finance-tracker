import io
import streamlit as st
from datetime import date, datetime
from PIL import Image
from components.cards import empty_state
from services.expense_service import (
    add_expense, update_expense, delete_expense, list_expenses,
    list_categories, add_category, category_icon,
)
from services.balance_service import add_balance, available_balance
from services import ocr_service
from database.database import get_setting
from utils.formatting import format_money, get_symbol
from utils.constants import BALANCE_SOURCES


def _uid():
    return st.session_state["user_id"]


def _cat_options():
    return [c["name"] for c in list_categories(_uid())]


def _cat_pretty(name: str) -> str:
    return f"{category_icon(_uid(), name)}  {name}"


def _inline_new_category():
    uid = _uid()
    with st.form("inline_add_cat", clear_on_submit=True):
        a, b = st.columns([3, 1])
        with a:
            name = st.text_input(
                "Name", placeholder="e.g. Groceries, Transport, Health",
                label_visibility="collapsed", key="inline_cat_name",
            )
        with b:
            icon = st.text_input(
                "Icon", value="📦", max_chars=4,
                label_visibility="collapsed", key="inline_cat_icon",
            )
        st.caption("Paste any emoji as the icon (🏠 🚗 💊 🎁 …). You can add many.")
        if st.form_submit_button("＋ Create category", use_container_width=True):
            n = name.strip()
            if not n:
                st.error("Please enter a name.")
            elif n.lower() in [c["name"].lower() for c in list_categories(uid)]:
                st.error(f"'{n}' already exists.")
            else:
                add_category(uid, n, icon.strip() or "📦")
                st.success(f"Added '{n}'. Choose it in the category dropdown below.")
                st.rerun()


def _add_expense_form(prefill: dict | None = None, key_prefix: str = "add"):
    prefill = prefill or {}
    uid = _uid()
    with st.form(f"{key_prefix}_expense_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            amt = st.number_input("Amount", min_value=0.0, step=1.0,
                                  value=float(prefill.get("amount") or 0.0),
                                  format="%.2f", key=f"{key_prefix}_amt")
        with col2:
            opts = _cat_options()
            default = prefill.get("category", opts[0] if opts else "Miscellaneous")
            idx = opts.index(default) if default in opts else 0
            cat = st.selectbox("Category", opts, format_func=_cat_pretty,
                               index=idx, key=f"{key_prefix}_cat")
        desc = st.text_input("Description", value=prefill.get("description", ""),
                             placeholder="e.g. Lunch at college",
                             key=f"{key_prefix}_desc")
        col3, col4 = st.columns([1, 1])
        with col3:
            dt = st.date_input("Date", value=prefill.get("date") or date.today(),
                               key=f"{key_prefix}_date")
        with col4:
            merchant = st.text_input("Merchant (optional)",
                                     value=prefill.get("merchant", ""),
                                     key=f"{key_prefix}_merch")
        if st.form_submit_button("Save Expense", use_container_width=True):
            if amt <= 0:
                st.error("Amount must be greater than 0.")
                return None
            add_expense(uid, amt, cat, desc, dt, merchant,
                        source=prefill.get("source", "manual"),
                        screenshot_path=prefill.get("screenshot_path", ""))
            st.success(
                f"Added {format_money(amt, get_setting(uid, 'currency', 'INR'))}. "
                f"Balance: {format_money(available_balance(uid), get_setting(uid, 'currency', 'INR'))}"
            )
    return None


def _add_balance_form():
    uid = _uid()
    with st.form("add_balance_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            amt = st.number_input("Amount", min_value=0.0, step=1.0,
                                  format="%.2f", key="addbal_amt")
        with c2:
            src = st.selectbox("Source", BALANCE_SOURCES, key="addbal_src")
        desc = st.text_input("Note (optional)", key="addbal_desc")
        dt = st.date_input("Date", value=date.today(), key="addbal_date")
        if st.form_submit_button("Add Balance", use_container_width=True):
            if amt <= 0:
                st.error("Amount must be greater than 0.")
                return
            add_balance(uid, amt, src, desc, dt)
            st.success(f"Added {format_money(amt, get_setting(uid, 'currency', 'INR'))} to balance.")
            st.rerun()


def _ocr_flow():
    uid = _uid()
    st.markdown("#### 📷 Scan payment screenshot")
    if not ocr_service.is_available():
        st.warning("Tesseract OCR is not installed on this server. Add expense manually.")
        return
    up = st.file_uploader("Upload PNG / JPG / WEBP",
                          type=["png", "jpg", "jpeg", "webp"], key="ocr_upload")
    if up:
        try:
            img = Image.open(io.BytesIO(up.getvalue()))
        except Exception:
            st.error("Could not read image. Please try another file.")
            return
        st.image(img, use_container_width=True, caption="Uploaded screenshot")
        with st.spinner("Extracting details…"):
            result = ocr_service.extract_from_image(img)
        if not result["ok"] and not result["amount"]:
            st.warning("We couldn't confidently read this screenshot. Please enter details manually.")
        prefill = {
            "amount": result["amount"] or 0.0,
            "category": result["category"],
            "description": (result["merchant"] or "")[:60],
            "merchant": result["merchant"],
            "date": result["date"] or date.today(),
            "source": "screenshot",
        }
        st.markdown("##### We found")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Amount**  \n{format_money(prefill['amount'] or 0, get_setting(uid, 'currency', 'INR'))}")
        c2.markdown(f"**Merchant**  \n{prefill['merchant'] or '—'}")
        c3.markdown(f"**Date**  \n{prefill['date']}")
        st.caption("Please confirm before adding. You can edit any field.")
        _add_expense_form(prefill=prefill, key_prefix="ocr")


def render():
    uid = _uid()
    currency = get_setting(uid, "currency", "INR")

    st.markdown("<h1 style='margin-bottom:0'>Expenses</h1>", unsafe_allow_html=True)
    st.caption("Track your spending. Add manually or scan a payment screenshot.")

    # Inline create-category helper — usable from any expense form on this page
    with st.expander("＋ New category", expanded=False):
        _inline_new_category()

    tab_add, tab_bal, tab_ocr, tab_hist = st.tabs(
        ["＋ Add Expense", "＋ Add Balance", "📷 Scan Screenshot", "🧾 History"]
    )

    with tab_add:
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        _add_expense_form(key_prefix="main")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_bal:
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        st.markdown(f"**Current balance:** {format_money(available_balance(uid), currency)}")
        _add_balance_form()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_ocr:
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        _ocr_flow()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_hist:
        _history_view(currency)


def _history_view(currency):
    uid = _uid()
    st.markdown("#### Transaction history")
    f1, f2, f3, f4 = st.columns([1, 1, 1, 1])
    with f1:
        cats = ["All"] + _cat_options()
        cat = st.selectbox("Category", cats, key="hist_cat")
    with f2:
        sort = st.selectbox("Sort by", ["Newest", "Oldest", "Highest", "Lowest"],
                            key="hist_sort")
    with f3:
        month_str = st.text_input("Month (YYYY-MM)", value="",
                                  key="hist_month", placeholder="2026-09")
    with f4:
        search = st.text_input("Search", key="hist_search",
                               placeholder="lunch, uber…")

    sort_map = {"Newest": "date_desc", "Oldest": "date_asc",
                "Highest": "amount_desc", "Lowest": "amount_asc"}
    y = m = None
    if month_str:
        try:
            dt = datetime.strptime(month_str, "%Y-%m")
            y, m = dt.year, dt.month
        except ValueError:
            st.warning("Use YYYY-MM (e.g. 2026-09).")

    items = list_expenses(uid, year=y, month=m, category=cat,
                          search=search or None, sort=sort_map[sort])
    if not items:
        empty_state("No expenses yet",
                    "Start tracking your spending by adding your first expense.", "🧾")
        return

    for e in items:
        icon = category_icon(uid, e["category"])
        cols = st.columns([1, 6, 2, 2])
        with cols[0]:
            st.markdown(
                f"<div style='font-size:22px;width:44px;height:44px;display:flex;"
                f"align-items:center;justify-content:center;background:var(--chip-bg);"
                f"border-radius:12px;'>{icon}</div>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            source_tag = ""
            if e['source'] == 'screenshot':
                source_tag = " · via screenshot"
            elif e['source'] == 'quickadd':
                source_tag = " · via quick add"
            elif e['source'] == 'recurring':
                source_tag = " · recurring"
            st.markdown(
                f"**{e['description'] or e['category']}**  \n"
                f"<span style='color:var(--muted);font-size:12px'>"
                f"{e['category']} · {e['date']}{source_tag}</span>",
                unsafe_allow_html=True,
            )
        with cols[2]:
            st.markdown(
                f"<div style='font-family:Fraunces,serif;font-weight:600;"
                f"font-size:18px;color:var(--primary);text-align:right'>"
                f"-{format_money(e['amount'], currency)}</div>",
                unsafe_allow_html=True,
            )
        with cols[3]:
            with st.popover("⋮", use_container_width=True):
                if st.button("Edit", key=f"edit_{e['id']}"):
                    st.session_state["editing_expense"] = e["id"]
                    st.rerun()
                if st.button("Delete", key=f"del_{e['id']}", type="secondary"):
                    delete_expense(uid, e["id"])
                    st.success("Deleted.")
                    st.rerun()

    eid = st.session_state.get("editing_expense")
    if eid:
        target = next((x for x in items if x["id"] == eid), None)
        if target:
            st.markdown("---")
            st.markdown("### Edit expense")
            with st.form(f"edit_form_{eid}"):
                c1, c2 = st.columns(2)
                with c1:
                    amt = st.number_input("Amount", value=float(target["amount"]),
                                          min_value=0.0, step=1.0)
                with c2:
                    opts = _cat_options()
                    idx = opts.index(target["category"]) if target["category"] in opts else 0
                    cat_new = st.selectbox("Category", opts, index=idx,
                                           format_func=_cat_pretty)
                desc = st.text_input("Description", value=target["description"])
                dt = st.date_input(
                    "Date", value=datetime.fromisoformat(target["date"]).date()
                )
                save, cancel = st.columns(2)
                if save.form_submit_button("Save", use_container_width=True):
                    update_expense(uid, eid, amount=amt, category=cat_new,
                                   description=desc, date=dt)
                    st.session_state.pop("editing_expense", None)
                    st.success("Updated.")
                    st.rerun()
                if cancel.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.pop("editing_expense", None)
                    st.rerun()
