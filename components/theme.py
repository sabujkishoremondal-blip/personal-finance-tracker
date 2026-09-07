"""Premium Gold + Black theme for Personal Finance."""

import streamlit as st


# ============================================================
# PREMIUM GOLD + BLACK PALETTE
# ============================================================

DARK = {
    "bg": "#070707",
    "surface": "#111111",
    "surface2": "#171717",
    "border": "rgba(212, 175, 55, 0.20)",

    "text": "#F5F0E6",
    "text_soft": "#D2C8B8",
    "muted": "#9C9384",

    "primary": "#D4AF37",
    "primary_d": "#B88A14",
    "primary_x": "#7A5A08",

    "accent": "#F0D77A",
    "success": "#65C18C",
    "danger": "#E56B6F",

    "chip_bg": "#19170F",
}


# ============================================================
# THEME HELPERS
# ============================================================

def current_theme_name() -> str:
    """The application uses one permanent dark theme."""
    return "dark"


def palette(name: str | None = None) -> dict:
    """Return the permanent Gold + Black application palette."""
    return DARK


# ============================================================
# GLOBAL CSS
# ============================================================

def inject_css():
    p = palette()

    css = f"""
    <style>

    /* ========================================================
       ROOT VARIABLES
       ======================================================== */

    :root {{
        --bg: {p['bg']};
        --surface: {p['surface']};
        --surface2: {p['surface2']};
        --border: {p['border']};

        --text: {p['text']};
        --text-soft: {p['text_soft']};
        --muted: {p['muted']};

        --primary: {p['primary']};
        --primary-d: {p['primary_d']};
        --primary-x: {p['primary_x']};

        --accent: {p['accent']};
        --success: {p['success']};
        --danger: {p['danger']};

        --chip-bg: {p['chip_bg']};
    }}


    /* ========================================================
       FONTS
       ======================================================== */

    @import url(
        'https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Manrope:wght@400;500;600;700;800&display=swap'
    );


    /* ========================================================
       GLOBAL APP
       ======================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    .stApp {{
        background:
            radial-gradient(
                circle at 85% 0%,
                rgba(212, 175, 55, 0.08),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #050505 0%,
                #090909 48%,
                #11100C 100%
            ) !important;

        color: var(--text) !important;

        font-family:
            'Manrope',
            system-ui,
            -apple-system,
            BlinkMacSystemFont,
            sans-serif !important;
    }}

    [data-testid="stAppViewContainer"] {{
        min-height: 100vh;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    [data-testid="stToolbar"] {{
        background: transparent !important;
    }}

    .block-container {{
        max-width: 1200px !important;
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }}


    /* ========================================================
       TYPOGRAPHY
       ======================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {{
        font-family:
            'Fraunces',
            Georgia,
            serif !important;

        color: var(--text) !important;

        letter-spacing: -0.02em !important;
    }}

    h1 {{
        font-size: 36px !important;
        line-height: 1.15 !important;
        font-weight: 600 !important;
    }}

    h2 {{
        font-size: 30px !important;
        line-height: 1.2 !important;
        font-weight: 600 !important;
    }}

    h3 {{
        font-size: 24px !important;
        line-height: 1.25 !important;
        font-weight: 600 !important;
    }}

    p {{
        color: var(--text-soft) !important;
    }}

    /* Do NOT globally style div/span.
       Streamlit uses these internally. */


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {{
        background:
            linear-gradient(
                180deg,
                #10100D 0%,
                #080808 100%
            ) !important;

        border-right:
            1px solid rgba(212, 175, 55, 0.14) !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem !important;
    }}

    [data-testid="stSidebar"] * {{
        color: var(--text) !important;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: rgba(212, 175, 55, 0.14) !important;
        margin: 20px 0 !important;
    }}


    /* ========================================================
       AUTHENTICATION HEADER
       ======================================================== */

    .auth-header {{
        max-width: 460px;
        margin: 40px auto 28px;
        text-align: center;
    }}

    .auth-logo {{
        width: 64px;
        height: 64px;
        margin: 0 auto 16px;

        border-radius: 20px;

        display: flex;
        align-items: center;
        justify-content: center;

        background:
            linear-gradient(
                135deg,
                #F0D77A 0%,
                #D4AF37 45%,
                #8A650F 100%
            );

        color: #080808;

        font-family:
            'Fraunces',
            Georgia,
            serif;

        font-size: 32px;

        font-weight: 700;

        box-shadow:
            0 8px 30px rgba(212, 175, 55, 0.20);
    }}

    .auth-header h1 {{
        margin: 0;

        color: var(--text) !important;

        font-family:
            'Fraunces',
            Georgia,
            serif !important;

        font-size: 36px !important;

        font-weight: 700 !important;
    }}

    .auth-header p {{
        margin-top: 8px;

        color: var(--muted) !important;

        font-size: 14px;
    }}


    /* ========================================================
       CARDS
       ======================================================== */

    .pf-card {{
        background:
            linear-gradient(
                145deg,
                rgba(20, 20, 20, 0.98),
                rgba(12, 12, 12, 0.98)
            ) !important;

        border:
            1px solid rgba(212, 175, 55, 0.16) !important;

        border-radius: 18px !important;

        padding: 22px !important;

        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.30) !important;

        margin-bottom: 18px !important;
    }}

    .pf-card-tight {{
        padding: 16px !important;
    }}


    /* ========================================================
       HERO BALANCE CARD
       ======================================================== */

    .pf-card-hero {{
        background:
            radial-gradient(
                circle at 85% 15%,
                rgba(240, 215, 122, 0.16),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #1A160A 0%,
                #0E0E0D 52%,
                #080808 100%
            ) !important;

        color: var(--text) !important;

        border:
            1px solid rgba(212, 175, 55, 0.28) !important;

        border-radius: 22px !important;

        padding: 28px !important;

        position: relative;

        box-shadow:
            0 15px 40px rgba(0, 0, 0, 0.40),
            inset 0 1px 0 rgba(240, 215, 122, 0.06) !important;

        margin-bottom: 22px !important;
    }}

    .pf-card-hero * {{
        color: var(--text) !important;
    }}

    .pf-card-hero .label {{
        letter-spacing: .16em !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        opacity: .72 !important;
        text-transform: uppercase !important;
    }}

    .pf-card-hero .balance {{
        font-family:
            'Fraunces',
            Georgia,
            serif !important;

        font-size: 56px !important;
        font-weight: 600 !important;
        line-height: 1.05 !important;

        margin: 10px 0 18px !important;
    }}

    .pf-card-hero .breakdown {{
        display: flex !important;
        gap: 28px !important;
        flex-wrap: wrap !important;
        margin-top: 10px !important;
    }}

    .pf-card-hero .breakdown .item .k {{
        font-size: 11px !important;
        opacity: .58 !important;
        text-transform: uppercase !important;
        letter-spacing: .12em !important;
    }}

    .pf-card-hero .breakdown .item .v {{
        font-size: 18px !important;
        font-weight: 700 !important;
        margin-top: 3px !important;
    }}

    .pf-card-hero.negative {{
        background:
            linear-gradient(
                135deg,
                #180B0C 0%,
                #090707 100%
            ) !important;

        border-color:
            rgba(229, 107, 111, 0.25) !important;
    }}

    .pf-warning {{
        margin-top: 16px !important;

        background:
            rgba(212, 175, 55, 0.08) !important;

        border:
            1px solid rgba(212, 175, 55, 0.18) !important;

        border-radius: 12px !important;

        padding: 11px 13px !important;

        font-size: 13px !important;
    }}


    /* ========================================================
       STAT CARDS
       ======================================================== */

    .stat {{
        display: flex !important;
        flex-direction: column !important;
        gap: 6px !important;
    }}

    .stat .k {{
        font-size: 11px !important;
        color: var(--muted) !important;
        text-transform: uppercase !important;
        letter-spacing: .12em !important;
        font-weight: 800 !important;
    }}

    .stat .v {{
        font-family:
            'Fraunces',
            Georgia,
            serif !important;

        color: var(--text) !important;

        font-size: 28px !important;
        font-weight: 600 !important;
    }}

    .stat .sub {{
        font-size: 12px !important;
        color: var(--text-soft) !important;
    }}


    /* ========================================================
       CATEGORY ROW
       ======================================================== */

    .cat-row {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;

        padding: 13px 0 !important;

        border-bottom:
            1px dashed rgba(212, 175, 55, 0.12) !important;
    }}

    .cat-row:last-child {{
        border-bottom: none !important;
    }}

    .cat-row .left {{
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }}

    .cat-row .icon {{
        font-size: 21px !important;
    }}

    .cat-row .name {{
        font-weight: 600 !important;
        color: var(--text) !important;
    }}

    .cat-row .amt {{
        font-family:
            'Fraunces',
            Georgia,
            serif !important;

        font-weight: 600 !important;
        font-size: 18px !important;
        color: var(--text) !important;
    }}


    /* ========================================================
       TRANSACTION CARD
       ======================================================== */

    .tx-card {{
        background:
            linear-gradient(
                145deg,
                #141414,
                #0E0E0E
            ) !important;

        border:
            1px solid rgba(212, 175, 55, 0.14) !important;

        border-radius: 16px !important;

        padding: 14px 16px !important;

        margin-bottom: 10px !important;

        display: flex !important;
        align-items: center !important;
        gap: 12px !important;

        transition:
            transform .15s ease,
            border-color .15s ease,
            background .15s ease !important;
    }}

    .tx-card:hover {{
        background: #181713 !important;

        border-color:
            rgba(212, 175, 55, 0.28) !important;

        transform: translateY(-1px) !important;
    }}

    .tx-card .ic {{
        font-size: 21px !important;

        width: 40px !important;
        height: 40px !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;

        background:
            var(--chip-bg) !important;

        border-radius: 12px !important;

        flex-shrink: 0 !important;
    }}

    .tx-card .mid {{
        flex: 1 !important;
        min-width: 0 !important;
    }}

    .tx-card .desc {{
        font-weight: 700 !important;
        color: var(--text) !important;
    }}

    .tx-card .meta {{
        font-size: 12px !important;
        color: var(--muted) !important;
        margin-top: 3px !important;
    }}

    .tx-card .amt {{
        font-family:
            'Fraunces',
            Georgia,
            serif !important;

        font-weight: 600 !important;
        font-size: 18px !important;
        white-space: nowrap !important;
    }}

    .tx-card .amt.neg {{
        color: #E5A0AA !important;
    }}

    .tx-card .amt.pos {{
        color: var(--success) !important;
    }}


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {{
        min-height: 44px !important;

        padding: 10px 20px !important;

        border-radius: 12px !important;

        border:
            1px solid rgba(240, 215, 122, 0.30) !important;

        background:
            linear-gradient(
                135deg,
                #D4AF37 0%,
                #B88A14 55%,
                #8A650F 100%
            ) !important;

        color: #080808 !important;

        font-family:
            'Manrope',
            sans-serif !important;

        font-weight: 800 !important;

        letter-spacing: .01em !important;

        box-shadow:
            0 6px 20px rgba(212, 175, 55, 0.16) !important;

        transition:
            transform .18s ease,
            box-shadow .18s ease,
            background .18s ease !important;
    }}

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background:
            linear-gradient(
                135deg,
                #F0D77A 0%,
                #D4AF37 55%,
                #B88A14 100%
            ) !important;

        color: #080808 !important;

        transform: translateY(-1px) !important;

        box-shadow:
            0 10px 28px rgba(212, 175, 55, 0.24) !important;
    }}

    .stButton > button:active,
    .stFormSubmitButton > button:active {{
        transform: translateY(0) !important;
    }}


    /* ========================================================
       SECONDARY BUTTONS
       ======================================================== */

    .stButton > button[kind="secondary"],
    .stDownloadButton > button[kind="secondary"] {{
        background:
            #151515 !important;

        color:
            var(--text) !important;

        border:
            1px solid rgba(212, 175, 55, 0.20) !important;

        box-shadow:
            none !important;
    }}

    .stButton > button[kind="secondary"]:hover,
    .stDownloadButton > button[kind="secondary"]:hover {{
        background:
            #1D1B15 !important;

        border-color:
            rgba(212, 175, 55, 0.38) !important;

        color:
            var(--accent) !important;

        box-shadow:
            none !important;
    }}


    /* ========================================================
       INPUTS
       ======================================================== */

    input,
    textarea,
    select,
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input {{
        background:
            var(--surface2) !important;

        color:
            var(--text) !important;

        -webkit-text-fill-color:
            var(--text) !important;

        border:
            1px solid rgba(212, 175, 55, 0.18) !important;

        border-radius:
            12px !important;

        box-shadow:
            none !important;

        caret-color:
            var(--accent) !important;
    }}

    input:focus,
    textarea:focus {{
        border-color:
            var(--primary) !important;

        box-shadow:
            0 0 0 1px var(--primary) !important;
    }}

    input::placeholder,
    textarea::placeholder {{
        color:
            #6F6A61 !important;

        opacity:
            1 !important;
    }}


    /* ========================================================
       BASEWEB INPUT CONTAINERS
       ======================================================== */

    [data-baseweb="input"] {{
        background:
            var(--surface2) !important;

        border:
            1px solid rgba(212, 175, 55, 0.18) !important;

        border-radius:
            12px !important;

        box-shadow:
            none !important;
    }}

    [data-baseweb="input"] > div {{
        background:
            transparent !important;

        border:
            none !important;

        box-shadow:
            none !important;
    }}

    [data-baseweb="textarea"] {{
        background:
            var(--surface2) !important;

        border:
            1px solid rgba(212, 175, 55, 0.18) !important;

        border-radius:
            12px !important;
    }}


    /* ========================================================
       SELECT / DROPDOWN
       ======================================================== */

    [data-baseweb="select"] {{
        background:
            var(--surface2) !important;

        border:
            1px solid rgba(212, 175, 55, 0.18) !important;

        border-radius:
            12px !important;

        box-shadow:
            none !important;
    }}

    [data-baseweb="select"] > div {{
        background:
            transparent !important;

        border:
            none !important;

        box-shadow:
            none !important;
    }}

    [data-baseweb="select"] div {{
        background:
            transparent !important;

        color:
            var(--text) !important;
    }}

    [data-baseweb="select"] span {{
        color:
            var(--text) !important;
    }}

    [data-baseweb="select"] svg {{
        fill:
            var(--accent) !important;
    }}


    /* ========================================================
       DROPDOWN POPUP
       ======================================================== */

    [data-baseweb="popover"] {{
        background:
            #111111 !important;

        border:
            1px solid rgba(212, 175, 55, 0.22) !important;

        border-radius:
            12px !important;

        box-shadow:
            0 15px 40px rgba(0, 0, 0, 0.55) !important;
    }}

    [data-baseweb="popover"] * {{
        color:
            var(--text) !important;
    }}

    [data-baseweb="menu"] {{
        background:
            #111111 !important;
    }}

    [role="listbox"] {{
        background:
            #111111 !important;
    }}

    [role="option"] {{
        background:
            #111111 !important;

        color:
            var(--text) !important;

        padding:
            10px 12px !important;
    }}

    [role="option"]:hover {{
        background:
            #1C1A13 !important;

        color:
            var(--accent) !important;
    }}

    [role="option"][aria-selected="true"] {{
        background:
            rgba(212, 175, 55, 0.16) !important;

        color:
            var(--accent) !important;
    }}


    /* ========================================================
       NUMBER INPUT + / -
       ======================================================== */

    [data-testid="stNumberInput"] {{
        background:
            transparent !important;
    }}

    [data-testid="stNumberInput"] > div {{
        background:
            transparent !important;

        border:
            none !important;
    }}

    [data-testid="stNumberInput"] button {{
        background:
            var(--surface2) !important;

        color:
            var(--text) !important;

        border:
            none !important;

        min-height:
            42px !important;

        box-shadow:
            none !important;
    }}

    [data-testid="stNumberInput"] button:hover {{
        background:
            #222016 !important;

        color:
            var(--accent) !important;
    }}


    /* ========================================================
       LABELS
       ======================================================== */

    .stTextInput label,
    .stNumberInput label,
    .stDateInput label,
    .stSelectbox label,
    .stTextArea label,
    .stFileUploader label,
    .stRadio label,
    .stCheckbox label {{
        color:
            var(--text-soft) !important;

        font-weight:
            600 !important;

        font-size:
            13px !important;

        letter-spacing:
            .01em !important;
    }}


    /* ========================================================
       TABS
       ======================================================== */

    .stTabs [data-baseweb="tab-list"] {{
        gap:
            4px !important;

        background:
            rgba(17, 17, 17, 0.92) !important;

        padding:
            5px !important;

        border-radius:
            14px !important;

        border:
            1px solid rgba(212, 175, 55, 0.16) !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius:
            10px !important;

        padding:
            9px 18px !important;

        font-weight:
            700 !important;

        color:
            var(--text-soft) !important;

        background:
            transparent !important;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color:
            var(--accent) !important;

        background:
            rgba(212, 175, 55, 0.07) !important;
    }}

    .stTabs [aria-selected="true"] {{
        background:
            linear-gradient(
                135deg,
                #D4AF37,
                #B88A14
            ) !important;

        color:
            #080808 !important;

        box-shadow:
            0 4px 14px rgba(212, 175, 55, 0.16) !important;
    }}

    .stTabs [aria-selected="true"] * {{
        color:
            #080808 !important;
    }}

    .stTabs [data-baseweb="tab-highlight"] {{
        background:
            var(--primary) !important;
    }}


    /* ========================================================
       RADIO BUTTONS
       ======================================================== */

    [data-testid="stRadio"] label {{
        color:
            var(--text-soft) !important;
    }}

    [data-testid="stRadio"] [role="radiogroup"] {{
        gap:
            8px !important;
    }}


    /* ========================================================
       CHECKBOX
       ======================================================== */

    [data-testid="stCheckbox"] label {{
        color:
            var(--text-soft) !important;
    }}


    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploaderDropzone"] {{
        background:
            var(--surface2) !important;

        border:
            1px dashed rgba(212, 175, 55, 0.28) !important;

        border-radius:
            14px !important;
    }}

    [data-testid="stFileUploaderDropzone"]:hover {{
        border-color:
            var(--primary) !important;

        background:
            #1A1811 !important;
    }}

    [data-testid="stFileUploaderDropzone"] * {{
        color:
            var(--text-soft) !important;
    }}


    /* ========================================================
       PROGRESS BAR
       ======================================================== */

    .stProgress > div > div > div > div {{
        background:
            linear-gradient(
                90deg,
                #B88A14,
                #F0D77A
            ) !important;
    }}

    .stProgress > div > div {{
        background:
            var(--surface2) !important;
    }}


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {{
        background:
            transparent !important;

        border:
            none !important;
    }}

    [data-testid="stMetricValue"] {{
        font-family:
            'Fraunces',
            Georgia,
            serif !important;

        color:
            var(--text) !important;
    }}

    [data-testid="stMetricLabel"] {{
        color:
            var(--muted) !important;

        font-weight:
            700 !important;

        text-transform:
            uppercase !important;

        letter-spacing:
            .1em !important;

        font-size:
            11px !important;
    }}


    /* ========================================================
       ALERTS
       ======================================================== */

    [data-testid="stAlert"] {{
        border-radius:
            12px !important;

        border:
            1px solid rgba(212, 175, 55, 0.18) !important;

        background:
            rgba(20, 20, 20, 0.90) !important;
    }}


    /* ========================================================
       EXPANDERS
       ======================================================== */

    [data-testid="stExpander"] {{
        background:
            var(--surface) !important;

        border:
            1px solid rgba(212, 175, 55, 0.16) !important;

        border-radius:
            14px !important;

        overflow:
            hidden !important;
    }}

    [data-testid="stExpander"] summary {{
        color:
            var(--text) !important;

        font-weight:
            600 !important;
    }}


    /* ========================================================
       DATAFRAMES / TABLES
       ======================================================== */

    [data-testid="stDataFrame"] {{
        border:
            1px solid rgba(212, 175, 55, 0.16) !important;

        border-radius:
            14px !important;

        overflow:
            hidden !important;
    }}


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {{
        border:
            none !important;

        border-top:
            1px solid rgba(212, 175, 55, 0.14) !important;

        margin:
            24px 0 !important;
    }}


    /* ========================================================
       LINKS
       ======================================================== */

    a {{
        color:
            var(--accent) !important;

        text-decoration:
            none !important;
    }}

    a:hover {{
        color:
            #F5E3A3 !important;

        text-decoration:
            underline !important;
    }}


    /* ========================================================
       CAPTIONS / SMALL TEXT
       ======================================================== */

    .stCaption,
    [data-testid="stCaptionContainer"] {{
        color:
            var(--muted) !important;
    }}


    /* ========================================================
       FORM CONTAINERS
       ======================================================== */

    [data-testid="stForm"] {{
        background:
            transparent !important;

        border:
            none !important;

        padding:
            0 !important;
    }}

    [data-testid="stForm"] > div {{
        border:
            none !important;
    }}


    /* ========================================================
       SCROLLBAR
       ======================================================== */

    ::-webkit-scrollbar {{
        width:
            8px;

        height:
            8px;
    }}

    ::-webkit-scrollbar-track {{
        background:
            var(--bg);
    }}

    ::-webkit-scrollbar-thumb {{
        background:
            #343026;

        border-radius:
            999px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background:
            #5A4D2D;
    }}


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 640px) {{

        .block-container {{
            padding:
                1rem
                .8rem
                4rem !important;
        }}

        h1 {{
            font-size:
                28px !important;
        }}

        h2 {{
            font-size:
                24px !important;
        }}

        h3 {{
            font-size:
                21px !important;
        }}

        .auth-header {{
            margin:
                25px auto 22px;
        }}

        .auth-header h1 {{
            font-size:
                30px !important;
        }}

        .auth-logo {{
            width:
                58px;

            height:
                58px;

            font-size:
                28px;
        }}

        .pf-card {{
            padding:
                16px !important;

            border-radius:
                16px !important;

            margin-bottom:
                14px !important;
        }}

        .pf-card-hero {{
            padding:
                20px !important;

            border-radius:
                18px !important;
        }}

        .pf-card-hero .balance {{
            font-size:
                40px !important;
        }}

        .pf-card-hero .breakdown {{
            gap:
                18px !important;
        }}

        .pf-card-hero .breakdown .item .v {{
            font-size:
                16px !important;
        }}

        .stat .v {{
            font-size:
                23px !important;
        }}

        .tx-card {{
            padding:
                12px !important;

            border-radius:
                14px !important;
        }}

        .tx-card .ic {{
            width:
                38px !important;

            height:
                38px !important;
        }}

        .tx-card .amt {{
            font-size:
                16px !important;
        }}

        .stButton > button,
        .stFormSubmitButton > button,
        .stDownloadButton > button {{
            min-height:
                46px !important;

            border-radius:
                12px !important;
        }}

        .stTabs [data-baseweb="tab"] {{
            padding:
                8px
                12px !important;

            font-size:
                13px !important;
        }}

        [data-baseweb="select"],
        [data-baseweb="input"] {{
            border-radius:
                12px !important;
        }}
    }}


    /* ========================================================
       TABLET
       ======================================================== */

    @media (min-width: 641px) and (max-width: 1024px) {{

        .block-container {{
            padding:
                1.5rem
                1.2rem
                4rem !important;
        }}

        .pf-card {{
            padding:
                20px !important;
        }}

        .pf-card-hero .balance {{
            font-size:
                48px !important;
        }}
    }}


    /* ========================================================
       HIDE STREAMLIT DEFAULT UI
       ======================================================== */

    footer {{
        visibility:
            hidden !important;
    }}

    #MainMenu {{
        visibility:
            hidden !important;
    }}


    </style>
    """

    st.markdown(css, unsafe_allow_html=True)