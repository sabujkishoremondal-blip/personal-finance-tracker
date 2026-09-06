"""Theme + global CSS. Two themes: light (ivory+burgundy) and dark (navy+burgundy)."""
import streamlit as st

LIGHT = {
    "bg":        "#F2F2ED",
    "surface":   "#FFFFFF",
    "surface2":  "#FBFAF6",
    "border":    "#E5E2D8",
    "text":      "#1A1613",
    "text_soft": "#5A544E",
    "muted":     "#8A8378",
    "primary":   "#8F002B",
    "primary_d": "#6F0022",
    "primary_x": "#58001B",
    "accent":    "#B23A5A",
    "success":   "#2F7D4F",
    "danger":    "#B00020",
    "chip_bg":   "#F5EFEA",
}

DARK = {
    "bg":        "#0E1220",
    "surface":   "#161B2E",
    "surface2":  "#1D2338",
    "border":    "#252B45",
    "text":      "#F5F1EC",
    "text_soft": "#B8B3AB",
    "muted":     "#7A7E92",
    "primary":   "#B23A5A",
    "primary_d": "#8F002B",
    "primary_x": "#6F0022",
    "accent":    "#D0778D",
    "success":   "#4AD295",
    "danger":    "#FF5C7A",
    "chip_bg":   "#232847",
}


def current_theme_name() -> str:
    return st.session_state.get("theme", "light")


def palette(name: str | None = None) -> dict:
    name = name or current_theme_name()
    return DARK if name == "dark" else LIGHT


def inject_css():
    p = palette()
    css = f"""
    <style>
    :root {{
        --bg:{p['bg']}; --surface:{p['surface']}; --surface2:{p['surface2']};
        --border:{p['border']}; --text:{p['text']}; --text-soft:{p['text_soft']};
        --muted:{p['muted']}; --primary:{p['primary']}; --primary-d:{p['primary_d']};
        --primary-x:{p['primary_x']}; --accent:{p['accent']}; --success:{p['success']};
        --danger:{p['danger']}; --chip-bg:{p['chip_bg']};
    }}
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Manrope:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Manrope', system-ui, -apple-system, sans-serif;
    }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{
        background: var(--surface);
        border-right: 1px solid var(--border);
    }}
    [data-testid="stSidebar"] * {{ color: var(--text) !important; }}
    .block-container {{ padding-top: 1.2rem; padding-bottom: 4rem; max-width: 1200px; }}

    h1,h2,h3,h4 {{ font-family: 'Fraunces', Georgia, serif; color: var(--text); letter-spacing:-0.01em; }}
    p, span, label, div {{ color: var(--text); }}

    /* PILL / TAG */
    .pf-chip {{
        display:inline-flex; align-items:center; gap:6px;
        background:var(--chip-bg); color:var(--text-soft);
        padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600;
        border:1px solid var(--border);
    }}

    /* CARDS */
    .pf-card {{
        background:var(--surface); border:1px solid var(--border);
        border-radius:20px; padding:22px 22px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }}
    .pf-card-tight {{ padding:16px; }}
    .pf-card-hero {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-x) 100%);
        color:#fff; border:none; border-radius:24px; padding:26px; position:relative;
        box-shadow: 0 8px 28px rgba(143,0,43,0.18);
    }}
    .pf-card-hero * {{ color:#fff !important; }}
    .pf-card-hero .label {{ letter-spacing:.14em; font-size:12px; font-weight:700; opacity:.85; text-transform:uppercase; }}
    .pf-card-hero .balance {{ font-family:'Fraunces',serif; font-size:56px; font-weight:600; line-height:1.05; margin:8px 0 14px; }}
    .pf-card-hero .breakdown {{ display:flex; gap:18px; flex-wrap:wrap; margin-top:8px; }}
    .pf-card-hero .breakdown .item .k {{ font-size:11px; opacity:.75; text-transform:uppercase; letter-spacing:.1em; }}
    .pf-card-hero .breakdown .item .v {{ font-size:18px; font-weight:600; }}

    .pf-card-hero.negative {{
        background: linear-gradient(135deg, #58001B 0%, #2A000C 100%);
    }}
    .pf-warning {{
        margin-top:14px; background: rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.25);
        border-radius:12px; padding:10px 12px; font-size:14px;
    }}

    /* STAT CARDS */
    .stat {{ display:flex; flex-direction:column; gap:6px; }}
    .stat .k {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.1em; font-weight:700; }}
    .stat .v {{ font-family:'Fraunces',serif; font-size:26px; font-weight:600; }}
    .stat .sub {{ font-size:12px; color:var(--text-soft); }}

    /* CATEGORY ROW */
    .cat-row {{
        display:flex; align-items:center; justify-content:space-between;
        padding:12px 0; border-bottom:1px dashed var(--border);
    }}
    .cat-row:last-child {{ border-bottom:none; }}
    .cat-row .left {{ display:flex; align-items:center; gap:10px; }}
    .cat-row .icon {{ font-size:22px; }}
    .cat-row .name {{ font-weight:600; }}
    .cat-row .amt {{ font-family:'Fraunces',serif; font-weight:600; font-size:18px; }}

    /* TX CARD (mobile-friendly) */
    .tx-card {{
        background:var(--surface); border:1px solid var(--border); border-radius:16px;
        padding:14px 16px; margin-bottom:10px; display:flex; align-items:center; gap:12px;
    }}
    .tx-card .ic {{ font-size:22px; width:40px; height:40px; display:flex; align-items:center;
        justify-content:center; background:var(--chip-bg); border-radius:12px; }}
    .tx-card .mid {{ flex:1; min-width:0; }}
    .tx-card .desc {{ font-weight:600; }}
    .tx-card .meta {{ font-size:12px; color:var(--muted); }}
    .tx-card .amt {{ font-family:'Fraunces',serif; font-weight:600; font-size:18px; }}
    .tx-card .amt.neg {{ color:var(--primary); }}
    .tx-card .amt.pos {{ color:var(--success); }}

    /* Streamlit primary button */
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
        background: var(--primary) !important; color:#fff !important;
        border:none !important; border-radius:14px !important;
        padding:10px 18px !important; font-weight:600 !important;
        min-height:44px; transition: all .18s ease;
        box-shadow: 0 2px 8px rgba(143,0,43,0.18);
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        background: var(--primary-d) !important; transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(143,0,43,0.28);
    }}
    .stButton > button[kind="secondary"] {{
        background: var(--surface2) !important; color:var(--text) !important;
        border:1px solid var(--border) !important; box-shadow:none !important;
    }}

    /* Inputs */
    input, textarea, select, .stTextInput input, .stNumberInput input, .stDateInput input {{
        background: var(--surface2) !important; color:var(--text) !important;
        border-radius:12px !important;
    }}
    [data-baseweb="input"], [data-baseweb="select"] {{
        background: var(--surface2) !important; border-radius:12px !important;
        border:1px solid var(--border) !important;
    }}
    [data-baseweb="select"] div {{ background:transparent !important; color:var(--text) !important; }}
    .stTextInput label, .stNumberInput label, .stDateInput label, .stSelectbox label,
    .stTextArea label, .stFileUploader label, .stRadio label {{
        color: var(--text-soft) !important; font-weight:600; font-size:13px;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px; background: var(--surface2); padding:6px; border-radius:14px;
        border:1px solid var(--border);
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius:10px; padding:8px 16px; font-weight:600;
        color:var(--text-soft); background: transparent;
    }}
    .stTabs [aria-selected="true"] {{ background: var(--primary); color:#fff !important; }}

    /* Progress bar */
    .stProgress > div > div > div > div {{ background: var(--primary) !important; }}

    /* Uploader */
    [data-testid="stFileUploaderDropzone"] {{
        background: var(--surface2); border:2px dashed var(--border); border-radius:14px;
    }}
    [data-testid="stFileUploaderDropzone"] * {{ color: var(--text-soft) !important; }}

    /* Metric */
    [data-testid="stMetric"] {{ background: transparent; }}
    [data-testid="stMetricValue"] {{ font-family:'Fraunces',serif; color:var(--text); }}
    [data-testid="stMetricLabel"] {{ color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:.1em; font-size:11px; }}

    /* Divider */
    hr {{ border-color: var(--border); }}

    /* Mobile responsive */
    @media (max-width: 640px) {{
        .block-container {{ padding: .6rem .8rem 4rem; }}
        .pf-card {{ padding:16px; border-radius:16px; }}
        .pf-card-hero {{ padding:20px; border-radius:20px; }}
        .pf-card-hero .balance {{ font-size:38px; }}
        h1 {{ font-size:26px !important; }}
        h2 {{ font-size:22px !important; }}
        .stat .v {{ font-size:22px; }}
    }}

    /* Hide streamlit default footer */
    footer {{ visibility:hidden; }}
    #MainMenu {{ visibility:hidden; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
