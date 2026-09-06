import streamlit as st
from datetime import date
from components.cards import stat_card, empty_state
from components.charts import donut, bar_categories, monthly_line
from services.analytics_service import month_report, compare_last_months
from services.recommendation_service import recommendations
from database.database import get_setting
from utils.formatting import format_money, month_label, get_symbol


def render():
    currency = get_setting("currency", "INR")
    sym = get_symbol(currency)

    st.markdown("<h1 style='margin-bottom:0'>Reports</h1>", unsafe_allow_html=True)
    st.caption("Monthly spending, category breakdowns, comparisons and savings tips.")

    today = date.today()
    c1, c2 = st.columns([1, 1])
    with c1:
        year = st.number_input("Year", value=today.year, step=1, min_value=2000, max_value=2100)
    with c2:
        month = st.selectbox("Month", list(range(1, 13)),
                             index=today.month - 1,
                             format_func=lambda m: month_label(int(year), m))

    rep = month_report(int(year), int(month))

    a, b, c = st.columns(3)
    with a: stat_card("Total Spent", format_money(rep["total_spent"], currency),
                       f"{rep['num_expenses']} expenses")
    with b: stat_card("Total Funds", format_money(rep["total_funds"], currency), "added + received")
    with c: stat_card("Remaining", format_money(rep["remaining"], currency), "funds - spent")

    a, b, c = st.columns(3)
    with a: stat_card("Avg / Day", format_money(rep["avg_daily"], currency), "so far")
    with b: stat_card("Top Category", f"{rep['highest_category']}",
                       format_money(rep["highest_amount"], currency))
    with c: stat_card("Categories", str(len(rep["categories"])), "used this month")

    st.write("")

    if not rep["categories"]:
        empty_state("No data for this month", "Add expenses to see reports.", "📊")
    else:
        left, right = st.columns([1, 1])
        with left:
            st.markdown("### Category share")
            with st.container():
                st.markdown('<div class="pf-card">', unsafe_allow_html=True)
                fig = donut(rep["categories"], sym)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("### Category totals")
            with st.container():
                st.markdown('<div class="pf-card">', unsafe_allow_html=True)
                fig = bar_categories(rep["categories"], sym)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("### Monthly trend")
    cmp_ = compare_last_months(6)
    if cmp_["data"] and len(cmp_["data"]) >= 1:
        with st.container():
            st.markdown('<div class="pf-card">', unsafe_allow_html=True)
            fig = monthly_line(cmp_["data"], sym)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            if cmp_["change_pct"] is not None:
                arrow = "▲" if cmp_["change_pct"] >= 0 else "▼"
                verb = "increased" if cmp_["change_pct"] >= 0 else "decreased"
                driver = f" The biggest change came from {cmp_['biggest_driver']}." if cmp_["biggest_driver"] else ""
                st.markdown(
                    f"<div style='margin-top:8px;color:var(--text-soft);'>"
                    f"{arrow} Spending {verb} by <b>{abs(cmp_['change_pct']):.1f}%</b> "
                    f"compared with the previous month.{driver}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        empty_state("Not enough months yet",
                    "The trend chart will appear once you have data from multiple months.", "📈")

    st.write("")
    st.markdown("### How can I save?")
    rec = recommendations(int(year), int(month))
    if rec["insufficient"]:
        empty_state("Building your insights…", rec["message"], "💡")
        return

    with st.container():
        st.markdown('<div class="pf-card">', unsafe_allow_html=True)
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;'>"
            f"<div><div style='color:var(--muted);text-transform:uppercase;letter-spacing:.1em;font-size:11px;font-weight:700;'>"
            f"Potential monthly saving</div>"
            f"<div style='font-family:Fraunces,serif;font-size:34px;font-weight:600;color:var(--primary);'>"
            f"{format_money(rec['potential_saving'], currency)}</div></div>"
            f"<div style='text-align:right;'>"
            f"<div style='color:var(--muted);text-transform:uppercase;letter-spacing:.1em;font-size:11px;font-weight:700;'>"
            f"Suggested next month target</div>"
            f"<div style='font-family:Fraunces,serif;font-size:24px;font-weight:600;'>"
            f"{format_money(rec['target_total'], currency)}</div></div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    for tip in rec["tips"]:
        saving_html = ""
        if tip.get("potential_saving"):
            saving_html = (
                f"<div style='font-family:Fraunces,serif;font-weight:600;"
                f"color:var(--primary);font-size:20px;white-space:nowrap;'>"
                f"Save {format_money(tip['potential_saving'], currency)}</div>"
            )
        st.markdown(
            f"<div class='pf-card' style='margin-top:10px;'>"
            f"<div style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;'>"
            f"<div><div style='font-weight:700;font-size:16px;'>💡 {tip['title']}</div>"
            f"<div style='color:var(--text-soft);margin-top:4px;'>{tip['body']}</div></div>"
            f"{saving_html}"
            f"</div></div>",
            unsafe_allow_html=True,
        )
