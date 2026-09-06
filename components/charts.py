import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.theme import palette


def _layout(fig, height=300):
    p = palette()
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, sans-serif", color=p["text"], size=13),
        margin=dict(l=10, r=10, t=30, b=10),
        height=height,
        showlegend=False,
    )
    return fig


def donut(categories: list, currency_symbol: str = "₹"):
    if not categories:
        return None
    p = palette()
    # burgundy family palette
    colors = ["#8F002B", "#B23A5A", "#6F0022", "#D0778D", "#58001B", "#E8A5B3", "#4A0015"]
    labels = [c["category"] for c in categories]
    values = [c["total"] for c in categories]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors[:len(labels)], line=dict(color=p["surface"], width=2)),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>" + currency_symbol + "%{value:,.0f} (%{percent})<extra></extra>",
    )])
    total = sum(values)
    fig.add_annotation(
        text=f"<b>{currency_symbol}{total:,.0f}</b><br><span style='font-size:11px;color:{p['muted']}'>Total</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=20, color=p["text"]),
    )
    return _layout(fig, height=320)


def bar_categories(categories: list, currency_symbol: str = "₹"):
    if not categories:
        return None
    p = palette()
    cats = list(reversed(categories))
    fig = go.Figure(go.Bar(
        x=[c["total"] for c in cats],
        y=[c["category"] for c in cats],
        orientation="h",
        marker=dict(color=p["primary"], line=dict(color=p["primary_d"], width=1)),
        text=[f"{currency_symbol}{c['total']:,.0f}" for c in cats],
        textposition="outside",
        textfont=dict(color=p["text"]),
    ))
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, tickfont=dict(size=13))
    return _layout(fig, height=max(180, 44 * len(cats) + 40))


def monthly_line(monthly: list, currency_symbol: str = "₹"):
    if not monthly:
        return None
    p = palette()
    xs = [m["ym"] for m in monthly]
    ys = [m["total"] for m in monthly]
    fig = go.Figure(go.Scatter(
        x=xs, y=ys, mode="lines+markers",
        line=dict(color=p["primary"], width=3, shape="spline"),
        marker=dict(size=9, color=p["primary_d"], line=dict(color="#fff", width=2)),
        fill="tozeroy",
        fillcolor=f"rgba(143,0,43,0.10)",
        hovertemplate="<b>%{x}</b><br>" + currency_symbol + "%{y:,.0f}<extra></extra>",
    ))
    fig.update_xaxes(showgrid=False, tickfont=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor=p["border"], tickfont=dict(size=11))
    return _layout(fig, height=280)
