import streamlit as st
from utils.formatting import format_money


def hero_balance(available: float, starting: float, added: float, spent: float, currency: str):
    negative = available < 0
    cls = "pf-card-hero negative" if negative else "pf-card-hero"
    warn = ""
    if negative:
        warn = (
            f'<div class="pf-warning">⚠️ You have exceeded your available balance by '
            f'{format_money(abs(available), currency)}.</div>'
        )
    html = f"""
    <div class="{cls}">
        <div class="label">Available Balance</div>
        <div class="balance">{format_money(available, currency)}</div>
        <div class="breakdown">
            <div class="item"><div class="k">Starting</div><div class="v">{format_money(starting, currency)}</div></div>
            <div class="item"><div class="k">Added</div><div class="v">{format_money(added, currency)}</div></div>
            <div class="item"><div class="k">Spent</div><div class="v">-{format_money(spent, currency)}</div></div>
        </div>
        {warn}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def stat_card(label: str, value: str, sub: str = ""):
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="pf-card pf-card-tight stat">'
        f'<div class="k">{label}</div><div class="v">{value}</div>'
        f'{sub_html}</div>',
        unsafe_allow_html=True,
    )


def transaction_card(icon: str, title: str, subtitle: str, amount_str: str,
                     positive: bool = False):
    cls = "pos" if positive else "neg"
    sign = "+" if positive else "-"
    st.markdown(
        f'<div class="tx-card">'
        f'<div class="ic">{icon}</div>'
        f'<div class="mid"><div class="desc">{title}</div>'
        f'<div class="meta">{subtitle}</div></div>'
        f'<div class="amt {cls}">{sign}{amount_str}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def empty_state(title: str, subtitle: str = "", icon: str = "✨"):
    st.markdown(
        f'<div class="pf-card" style="text-align:center; padding:36px 20px;">'
        f'<div style="font-size:36px; margin-bottom:8px;">{icon}</div>'
        f'<div style="font-family:Fraunces,serif; font-size:20px; font-weight:600;">{title}</div>'
        f'<div style="color:var(--muted); margin-top:6px;">{subtitle}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
