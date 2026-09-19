import json
import base64
import os
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
BG_PATH   = os.path.join(BASE_DIR, "assets", "bg.png")


@st.cache_data
def _logo_base64():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


@st.cache_data
def _bg_base64():
    if os.path.exists(BG_PATH):
        with open(BG_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


# ──────────────────────────────────────────────────────────────────
#  INJECT GLOBAL CSS — Dark "Vault" theme (neon green + gold accents)
# ──────────────────────────────────────────────────────────────────
def inject_css():
    st.html(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;500;600;700;800;900&display=swap');

:root {{
    --bg:        #FFFFFF;
    --bg2:       #F8FAFC;
    --sidebar:   #FFFFFF;
    --card:      rgba(255,255,255,0.95);
    --border:    rgba(99,102,241,0.15);
    --primary:   #4F46E5;
    --primary-lt:#818CF8;
    --primary-dk:#3730A3;
    --accent:    #6366F1;
    --gold:      #E8A838;
    --gold-lt:   #F5C55E;
    --text:      #F0F0F0;
    --text-secondary: #64748B;
    --muted:     #94A3B8;
    --danger:    #EF4444;
    --success:   #22C55E;
    --radius:    14px;
    --radius-lg: 20px;
}}

/* GLOBAL RESET — classy dark "vault" theme (matches .streamlit/config.toml) */
html, body, [class*="css"] {{
    font-family: 'Inter','Outfit',-apple-system,sans-serif !important;
    color: #F0F0F0 !important;
}}

/* DARK GRADIENT BACKGROUND on entire app */
.stApp, .stApp > div, [data-testid="stAppViewContainer"] {{
    background: radial-gradient(ellipse at 20% 0%, #0D1325 0%, #0B0E17 45%, #05070C 100%) !important;
    background-attachment: fixed !important;
}}

[data-testid="stAppViewContainer"] > .main {{
    position: relative;
    z-index: 1;
}}

/* HIDE ALL STREAMLIT CHROME — toolbar, 3-dot menu, deploy, settings, trash, color themes, recording */
#MainMenu, footer,
.stDeployButton, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
button[title="View app in Streamlit Cloud"],
button[title="Record a screencast"], button[title="Settings"],
button[title="Report a bug"), button[title="About"],
button[aria-label="Manage app"], button[title="Manage app"],
[data-testid="stSidebarNavItems"], [data-testid="stSidebarNav"],
nav[data-testid="stSidebarNav"],
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"],
.css-17lntkn, .css-pkbazv, .st-emotion-cache-pbvh6p,
[data-testid="stToolbarActions"], [aria-label="Toolbar actions"],
[data-testid="stToolbarActionButton"],
.stActionButton, [data-testid="stAppToolbar"],
button[title="Open in Streamlit Community Cloud"],
button[title="App is not running"],
[data-testid="stMainMenuPopover"], .stMainMenu,
[class*="toolbar"], [class*="Toolbar"],
[data-testid="baseButton-header"],
div[class*="StatusWidget"], div[class*="stDecoration"] {{
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    opacity: 0 !important;
}}

/* Keep the header bar ONLY for the sidebar toggle button */
header[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
    height: auto !important;
    min-height: 0 !important;
}}
/* Hide most header children but NOT buttons (toggle lives there) */
header[data-testid="stHeader"] > div:not(:has(button)) {{
    display: none !important;
}}
/* Always show the sidebar collapsed control — this is the re-open button! */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[data-testid="collapsedControl"],
header[data-testid="stHeader"] button {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}}
/* Hide header items that are NOT the sidebar toggle */
header[data-testid="stHeader"] [data-testid="stToolbarActions"],
header[data-testid="stHeader"] [data-testid="stStatusWidget"] {{
    display: none !important;
}}

/* Style the sidebar toggle button to match our theme */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="collapsedControl"] button,
header[data-testid="stHeader"] button {{
    background: rgba(2,5,8,0.90) !important;
    border: 1px solid rgba(57,255,20,0.35) !important;
    border-radius: 8px !important;
    color: #39FF14 !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.60), 0 0 8px rgba(57,255,20,0.20) !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="collapsedControl"] button:hover,
header[data-testid="stHeader"] button:hover {{
    background: rgba(57,255,20,0.15) !important;
    border-color: #39FF14 !important;
    box-shadow: 0 0 16px rgba(57,255,20,0.50) !important;
}}

/* STYLE st.page_link in sidebar as custom nav items */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {{
    margin: 1px 6px !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 11px 14px !important;
    border-radius: 12px !important;
    border: 1px solid transparent !important;
    text-decoration: none !important;
    color: #94A3B8 !important;
    font-size: 0.74rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
    transition: all 0.2s ease !important;
    background: transparent !important;
}}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
    background: rgba(57,255,20,0.08) !important;
    border-color: rgba(57,255,20,0.20) !important;
    color: #39FF14 !important;
}}

/* Hide raw button labels from nav buttons — collapse to zero height */
section[data-testid="stSidebar"] .stButton > button:not(:last-child) {{
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    font-size: 0 !important;
    line-height: 0 !important;
    display: block !important;
}}

/* SCROLLBAR */
::-webkit-scrollbar {{ width:5px; }}
::-webkit-scrollbar-track {{ background:rgba(0,0,0,0.3); }}
::-webkit-scrollbar-thumb {{ background:rgba(57,255,20,0.35); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:var(--green); }}

/* MAIN CONTENT */
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1160px !important;
}}

/* SIDEBAR */
section[data-testid="stSidebar"] {{
    background: rgba(2,5,8,0.97) !important;
    border-right: 1px solid rgba(57,255,20,0.12) !important;
    box-shadow: 4px 0 40px rgba(0,0,0,0.70) !important;
    backdrop-filter: blur(20px) !important;
}}
/* Sidebar text — do NOT blanket-override inputs/labels here */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{ color: var(--text); }}

/* NAV SIDEBAR BRAND */
.sb-brand {{
    padding: 20px 18px 16px;
    margin-bottom: 8px;
    border-bottom: 1px solid rgba(57,255,20,0.15);
}}
.sb-brand .logo-box {{
    background:#fff; border-radius:10px;
    padding:7px 10px; display:inline-block;
    margin-bottom:10px;
    box-shadow:0 0 20px rgba(57,255,20,0.25);
}}
.sb-brand .logo-box img {{ height:40px; display:block; }}
.sb-brand .brand-name {{
    font-family:'Outfit',sans-serif;
    font-size:0.90rem; font-weight:800;
    color:#F0F0F0 !important; line-height:1.25;
}}
.sb-brand .brand-tag {{
    font-size:0.65rem; font-weight:700;
    color:var(--green) !important;
    text-transform:uppercase; letter-spacing:.12em;
    margin-top:3px;
}}

/* NAV SECTION LABEL */
.nav-label {{
    font-size:0.60rem; font-weight:800;
    color:rgba(148,163,184,0.55) !important;
    text-transform:uppercase; letter-spacing:.18em;
    padding: 16px 18px 8px;
}}

/* NAV ITEM — inactive */
.nav-item {{
    display:flex; align-items:center; gap:12px;
    padding:12px 18px;
    margin:2px 10px;
    border-radius:12px;
    cursor:pointer;
    transition:all 0.2s ease;
    text-decoration:none;
}}
.nav-item:hover {{
    background:rgba(57,255,20,0.08);
    border:1px solid rgba(57,255,20,0.20);
}}
.nav-item .nav-icon {{
    font-size:1.1rem; width:22px; text-align:center;
}}
.nav-item .nav-text {{
    font-size:0.78rem; font-weight:700;
    color:#94A3B8 !important;
    text-transform:uppercase; letter-spacing:.08em;
}}

/* NAV ITEM — active */
.nav-item.active {{
    background: var(--green) !important;
    box-shadow: 0 0 20px rgba(57,255,20,0.45), 0 4px 16px rgba(0,0,0,0.4);
    margin:2px 10px;
}}
.nav-item.active .nav-text {{
    color: #020508 !important;
    font-weight:900 !important;
}}
.nav-item.active .nav-icon {{ filter:brightness(0); }}

/* USER CARD IN SIDEBAR */
.sb-user {{
    background:rgba(57,255,20,0.05);
    border:1px solid rgba(57,255,20,0.15);
    border-left:3px solid var(--green);
    border-radius:12px; padding:12px 14px;
    margin:14px 10px 0;
}}
.sb-user .u-name {{
    font-size:0.88rem; font-weight:800; color:#F0F0F0 !important;
}}
.sb-user .u-role {{
    font-size:0.62rem; font-weight:700;
    color:var(--green) !important;
    text-transform:uppercase; letter-spacing:.10em; margin-top:2px;
}}
.sb-user .u-bell {{
    font-size:0.72rem; color:#94A3B8 !important; margin-top:4px;
}}

/* GLASSMORPHISM CARD */
.glass-card {{
    background: rgba(4,12,28,0.85) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(57,255,20,0.14) !important;
    border-radius: var(--radius-lg) !important;
    padding: 20px 22px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.50) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
.glass-card:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 14px 44px rgba(57,255,20,0.12) !important;
    border-color: rgba(57,255,20,0.28) !important;
}}

/* STAT CARD */
.stat-card {{
    background: linear-gradient(145deg,rgba(4,12,28,0.95),rgba(8,18,36,0.95)) !important;
    border: 1px solid rgba(57,255,20,0.18) !important;
    border-radius: var(--radius-lg) !important;
    padding: 18px 16px 14px !important;
    box-shadow: 4px 4px 16px rgba(0,0,0,0.5),-2px -2px 8px rgba(255,255,255,0.02) !important;
    transition: transform 0.2s, border-color 0.2s !important;
}}
.stat-card:hover {{
    transform: scale(1.03) !important;
    border-color: var(--green) !important;
    box-shadow: 0 0 24px rgba(57,255,20,0.20) !important;
}}
.stat-card .stat-icon {{ font-size:1.6rem; margin-bottom:6px; }}
.stat-card .stat-value {{
    font-size:1.85rem !important; font-weight:900 !important;
    color:#FFFFFF !important; letter-spacing:-0.02em; line-height:1.1;
}}
.stat-card .stat-label {{
    font-size:0.68rem !important; font-weight:700 !important;
    color:var(--muted) !important;
    text-transform:uppercase; letter-spacing:.08em;
}}

/* INPUTS — dark background, light text */
.stTextInput input, .stTextArea textarea,
input[type=text], input[type=email],
input[type=password], input[type=number] {{
    background: rgba(4,8,16,0.90) !important;
    color: #F0F0F0 !important;
    border: 1.5px solid rgba(57,255,20,0.20) !important;
    border-radius: 10px !important;
    font-size: 0.90rem !important;
    padding: 10px 14px !important;
}}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{
    color: rgba(148,163,184,0.60) !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px rgba(57,255,20,0.12) !important;
}}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stNumberInput label, .stDateInput label, .stTimeInput label, .stSlider label {{
    color: rgba(240,240,240,0.70) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .05em !important;
}}
div[data-baseweb="select"] > div {{
    background: rgba(4,8,16,0.90) !important;
    border: 1.5px solid rgba(57,255,20,0.20) !important;
    border-radius: 10px !important;
    color: #F0F0F0 !important;
}}
/* Dropdown menu items */
[data-baseweb="menu"], [data-baseweb="popover"] {{
    background: #0D1325 !important;
    border: 1px solid rgba(57,255,20,0.20) !important;
}}
[data-baseweb="option"] {{
    background: #0D1325 !important;
    color: #F0F0F0 !important;
}}
[data-baseweb="option"]:hover {{
    background: rgba(57,255,20,0.10) !important;
}}
/* White / light-background native elements — force dark text */
select, option {{
    background: #0D1325 !important;
    color: #F0F0F0 !important;
}}
/* Streamlit checkbox, radio on white bg — dark label text */
.stCheckbox span, .stRadio span {{
    color: rgba(240,240,240,0.80) !important;
}}
/* DataFrames have white bg by default — ensure dark text */
.stDataFrame td, .stDataFrame th {{
    color: #0D1325 !important;
    background: rgba(240,244,255,0.96) !important;
    font-weight: 600 !important;
}}
.stDataFrame thead th {{
    background: rgba(57,255,20,0.12) !important;
    color: #0a1a05 !important;
    font-weight: 800 !important;
}}
/* Expander header text on light backgrounds */
.stExpander details summary span {{
    color: #E8E8E8 !important;
}}
/* Tab text contrast */
.stTabs [data-baseweb="tab"] span {{
    color: inherit !important;
}}
/* Alert / info box text — keep visible */
[data-testid="stAlert"] p,
[data-testid="stAlert"] div {{
    color: #1a1a2e !important;
}}
[data-testid="stAlert"][data-baseweb="notification"] {{
    background: rgba(240,244,255,0.95) !important;
}}
/* Caption text */
.stCaption, [data-testid="stCaptionContainer"] p {{
    color: #94A3B8 !important;
}}
/* Code blocks — dark bg dark text issue */
.stCodeBlock pre, .stCodeBlock code {{
    color: #D4EDDA !important;
    background: rgba(4,8,16,0.92) !important;
}}

/* BUTTONS */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
    font-family:'Inter',sans-serif !important;
    font-size:0.85rem !important; font-weight:700 !important;
    border-radius:10px !important; padding:10px 20px !important;
    cursor:pointer !important;
    transition:all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
    background:rgba(4,12,28,0.90) !important;
    border:1.5px solid rgba(57,255,20,0.25) !important;
    color:#E0E0E0 !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    transform:translateY(-2px) !important;
    background:rgba(57,255,20,0.10) !important;
    border-color:var(--green) !important;
    color:var(--green) !important;
    box-shadow:0 6px 20px rgba(57,255,20,0.22) !important;
}}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
    background:var(--green) !important;
    border:none !important; color:#020508 !important;
    font-weight:900 !important;
    box-shadow:0 4px 20px rgba(57,255,20,0.40) !important;
}}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
    background:var(--green-lt) !important;
    box-shadow:0 8px 28px rgba(57,255,20,0.60) !important;
    transform:translateY(-2px) !important;
}}

/* TABS */
.stTabs [data-baseweb="tab-list"] {{
    background:rgba(4,8,16,0.80) !important;
    border-radius:var(--radius) !important; padding:4px !important;
    gap:3px !important; border:1px solid rgba(57,255,20,0.10) !important;
}}
.stTabs [data-baseweb="tab"] {{
    background:transparent !important; border-radius:10px !important;
    padding:8px 14px !important; font-weight:600 !important;
    font-size:0.82rem !important; color:var(--muted) !important;
    border:none !important;
}}
.stTabs [data-baseweb="tab"]:hover {{ color:var(--green) !important; }}
.stTabs [aria-selected="true"] {{
    background:var(--green) !important; color:#020508 !important;
    font-weight:900 !important;
    box-shadow:0 4px 14px rgba(57,255,20,0.35) !important;
}}

/* LOT CARD */
.lot-card {{
    background:rgba(4,12,28,0.85);
    border:1px solid rgba(57,255,20,0.14);
    border-radius:18px; overflow:hidden; margin-bottom:18px;
    box-shadow:0 8px 28px rgba(0,0,0,0.50);
    transition:transform 0.25s, box-shadow 0.25s, border-color 0.25s;
}}
.lot-card:hover {{
    transform:translateY(-4px);
    box-shadow:0 16px 40px rgba(57,255,20,0.18);
    border-color:rgba(57,255,20,0.38);
}}
.lot-card img {{ width:100%; height:160px; object-fit:cover; display:block; }}
.lot-card-body {{ padding:14px 16px; }}
.lot-card-title {{ font-weight:800 !important; font-size:1.02rem !important; color:#F0F0F0 !important; margin-bottom:3px; }}
.lot-card-sub {{ color:var(--muted) !important; font-size:0.80rem !important; margin-bottom:10px; }}
.lot-tags {{ display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px; }}

/* BADGES */
.badge {{
    display:inline-block; padding:3px 10px;
    border-radius:999px; font-size:0.70rem;
    font-weight:700 !important; letter-spacing:.03em; text-transform:uppercase;
}}
.badge-green  {{ background:rgba(57,255,20,0.10);  color:#39FF14 !important; border:1px solid rgba(57,255,20,0.28); }}
.badge-red    {{ background:rgba(239,68,68,0.10);   color:#FCA5A5 !important; border:1px solid rgba(239,68,68,0.28); }}
.badge-indigo {{ background:rgba(99,102,241,0.10);  color:#A5B4FC !important; border:1px solid rgba(99,102,241,0.28); }}
.badge-orange {{ background:rgba(232,168,56,0.10);  color:#F5C55E !important; border:1px solid rgba(232,168,56,0.28); }}
.badge-gray   {{ background:rgba(148,163,184,0.08); color:#94A3B8 !important; border:1px solid rgba(148,163,184,0.18); }}

.price-tag {{ font-weight:900 !important; color:var(--gold) !important; font-size:1.1rem !important; }}
.muted {{ color:var(--muted) !important; }}

/* NOTIFICATION */
.notif-item {{
    padding:12px 14px; border-radius:12px; margin-bottom:8px;
    border-left:3px solid var(--green);
    background:rgba(4,12,28,0.85);
}}
.notif-time {{ font-size:0.70rem !important; color:var(--muted) !important; margin-top:3px; }}

/* ALERTS */
.stAlert, div[data-testid="stAlert"] {{ border-radius:var(--radius) !important; }}

/* DATA TABLE */
.stDataFrame {{ border-radius:var(--radius) !important; overflow:hidden !important; }}
.stDataFrame thead th {{
    background:rgba(57,255,20,0.10) !important;
    color:var(--green) !important; font-weight:700 !important;
    font-size:0.76rem !important; text-transform:uppercase !important;
}}

/* EXPANDER */
.stExpander {{
    background:rgba(4,12,28,0.75) !important;
    border:1px solid rgba(57,255,20,0.12) !important;
    border-radius:var(--radius) !important;
}}

/* CONTAINER BORDERS */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background:rgba(4,12,28,0.80) !important;
    border:1px solid rgba(57,255,20,0.12) !important;
    border-radius:var(--radius-lg) !important;
    box-shadow:0 8px 32px rgba(0,0,0,0.40) !important;
    padding:20px !important;
}}

/* TYPOGRAPHY */
h1 {{ font-size:1.85rem !important; font-weight:900 !important; color:#F0F0F0 !important; letter-spacing:-0.02em !important; }}
h2 {{ font-size:1.45rem !important; font-weight:800 !important; color:#E8E8E8 !important; }}
h3 {{ font-size:1.15rem !important; font-weight:700 !important; color:#D8D8D8 !important; }}
p, li {{ color:rgba(240,240,240,0.75) !important; font-size:0.88rem !important; line-height:1.6 !important; }}
hr {{ border:none !important; height:1px !important; background:rgba(57,255,20,0.12) !important; }}
strong, b {{ color:#F0F0F0 !important; }}
code {{ background:rgba(255,255,255,0.08) !important; color:#E8E8E8 !important; border-radius:5px !important; padding:2px 6px !important; }}

/* ANIMATIONS */
@keyframes pulse-dot {{
    0%,100% {{ opacity:1; transform:scale(1); }}
    50% {{ opacity:0.3; transform:scale(1.8); }}
}}
@keyframes glow-ring {{
    0%,100% {{ box-shadow:0 0 8px rgba(57,255,20,0.50); }}
    50% {{ box-shadow:0 0 20px rgba(57,255,20,0.85); }}
}}
.live-dot {{
    width:9px; height:9px; border-radius:50%;
    background:var(--green); display:inline-block;
    vertical-align:middle; margin-right:5px;
    animation:pulse-dot 1.8s infinite, glow-ring 1.8s infinite;
}}

/* LOGOUT BUTTON */
div.element-container:has(button[key="logout_sidebar"]) {{
    position:fixed !important; bottom:16px !important;
    left:10px !important; width:220px !important; z-index:1000 !important;
}}
button[key="logout_sidebar"] {{
    background:rgba(239,68,68,0.08) !important;
    border:1px solid rgba(239,68,68,0.25) !important;
    color:#FCA5A5 !important; font-weight:700 !important;
}}
button[key="logout_sidebar"]:hover {{
    background:rgba(239,68,68,0.22) !important;
    border-color:#EF4444 !important; color:#fff !important;
}}

/* RESPONSIVE */
@media(max-width:640px) {{
    .block-container {{ padding-left:0.8rem !important; padding-right:0.8rem !important; }}
    h1 {{ font-size:1.4rem !important; }}
}}
</style>""")


# ──────────────────────────────────────────────────────────────────
#  SITE-WIDE HEADER — S.A.I. style (Screenshot 3)
# ──────────────────────────────────────────────────────────────────
def inject_top_header(page_name="", show_login_btn=False):
    logo_b64 = _logo_base64()
    logo_html = (
        f'<img src="data:image/png;base64,{logo_b64}" '
        'style="height:34px;display:block;" />'
    ) if logo_b64 else "🅿️"

    login_btn = ""
    if show_login_btn:
        login_btn = (
            '<a href="#sign-in" style="'
            'background:#39FF14;color:#020508;'
            'font-size:0.72rem;font-weight:900;font-family:Outfit,sans-serif;'
            'text-transform:uppercase;letter-spacing:.10em;'
            'padding:8px 18px;border-radius:8px;text-decoration:none;'
            'box-shadow:0 0 18px rgba(57,255,20,0.55);'
            'white-space:nowrap;cursor:pointer;display:inline-block;'
            '">VAULT LOGIN</a>'
        )

    menu_icon = (
        '<div style="'
        'width:34px;height:34px;border-radius:8px;'
        'border:1px solid rgba(57,255,20,0.30);'
        'display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;'
        'cursor:pointer;background:rgba(57,255,20,0.05);'
        '">'
        '<div style="width:14px;height:2px;background:#39FF14;border-radius:1px;"></div>'
        '<div style="width:14px;height:2px;background:#39FF14;border-radius:1px;"></div>'
        '<div style="width:14px;height:2px;background:#39FF14;border-radius:1px;"></div>'
        '</div>'
    )

    st.html(
        # ── Header wrapper
        '<div style="'
        'position:sticky;top:0;left:0;right:0;z-index:9999;'
        'display:flex;align-items:center;justify-content:space-between;'
        'padding:10px 28px;'
        'background:rgba(2,4,8,0.97);'
        'border-bottom:1px solid rgba(57,255,20,0.22);'
        'backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);'
        'box-shadow:0 4px 32px rgba(0,0,0,0.80);'
        'margin:-1.5rem -1rem 1.5rem -1rem;'
        '">'

        # ── LEFT: S.A.I. logo + name
        '<div style="display:flex;align-items:center;gap:10px;">'
        f'<div style="background:#fff;border-radius:9px;padding:4px 8px;'
        f'box-shadow:0 0 16px rgba(57,255,20,0.28);">{logo_html}</div>'
        '<div>'
        '<div style="font-family:Outfit,sans-serif;font-size:1.05rem;font-weight:900;'
        'color:#F0F0F0;letter-spacing:0.06em;line-height:1.0;">S.A.I.</div>'
        '<div style="font-size:0.55rem;font-weight:700;color:rgba(148,163,184,0.65);'
        'text-transform:uppercase;letter-spacing:.12em;margin-top:1px;">Smart AI Interface</div>'
        '</div>'
        '</div>'

        # ── CENTER: tagline (protect every parking spot / access without limits)
        '<div style="position:absolute;left:50%;transform:translateX(-50%);text-align:center;">'
        '<div style="font-size:0.72rem;font-weight:900;color:#39FF14;'
        'text-transform:uppercase;letter-spacing:.14em;'
        'text-shadow:0 0 12px rgba(57,255,20,0.50);">PROTECT EVERY PARKING SPOT.</div>'
        '<div style="font-size:0.55rem;font-weight:600;color:rgba(148,163,184,0.65);'
        'text-transform:uppercase;letter-spacing:.12em;margin-top:2px;">ACCESS WITHOUT LIMITS.</div>'
        '</div>'

        # ── RIGHT: login button + hamburger menu
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'{login_btn}'
        '<div style="display:flex;align-items:center;gap:6px;'
        'background:rgba(57,255,20,0.06);border:1px solid rgba(57,255,20,0.18);'
        'border-radius:8px;padding:6px 12px;cursor:pointer;">'
        '<span style="font-size:0.70rem;font-weight:700;color:#94A3B8;'
        'text-transform:uppercase;letter-spacing:.08em;">ON</span>'
        '<div style="width:8px;height:8px;border-radius:50%;background:#39FF14;'
        'box-shadow:0 0 8px rgba(57,255,20,0.80);'
        'animation:pulse-dot 1.8s infinite;"></div>'
        '</div>'
        f'{menu_icon}'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


def top_header(title, subtitle="", pill=None):
    pill_html = (
        f'<div style="background:rgba(57,255,20,0.10);border:1px solid rgba(57,255,20,0.30);'
        f'color:#39FF14;padding:7px 18px;border-radius:999px;font-size:0.80rem;'
        f'font-weight:700;white-space:nowrap;">{pill}</div>'
    ) if pill else ""
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'padding:20px 28px;margin:-1rem -1rem 1.5rem -1rem;'
        'background:linear-gradient(135deg,rgba(2,8,20,0.95),rgba(5,14,32,0.95));'
        'border-radius:0 0 22px 22px;'
        'border-bottom:2px solid rgba(57,255,20,0.30);'
        'box-shadow:0 10px 36px rgba(0,0,0,0.55);backdrop-filter:blur(20px);'
        '">'
        f'<div><h1 style="font-family:Outfit,sans-serif;font-size:1.9rem;font-weight:900;'
        f'color:#FFFFFF;margin:0;letter-spacing:-0.02em;">{title}</h1>'
        f'<p style="color:rgba(148,163,184,0.80);margin:4px 0 0;font-size:0.85rem;">{subtitle}</p></div>'
        f'{pill_html}'
        '</div>',
        unsafe_allow_html=True
    )


def rating_stars(rating: float) -> str:
    full = int(round(rating))
    return "★" * full + "☆" * (5 - full) + f"  {rating:.1f}"


def badge(text, kind="indigo"):
    return f'<span class="badge badge-{kind}">{text}</span>'


def stat_card(icon, label, value):
    st.markdown(
        f'<div class="stat-card">'
        f'<div class="stat-icon">{icon}</div>'
        f'<div class="stat-value">{value}</div>'
        f'<div class="stat-label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def prediction_badge(label, confidence):
    if label is None:
        st.markdown(badge("Model unavailable", "gray"))
        return
    kind = "badge-green" if label == "Vacant" else "badge-red"
    icon = "🟢" if label == "Vacant" else "🔴"
    st.markdown(
        f'{badge(f"{icon} {label}", kind)} '
        f'<span style="font-size:0.76rem;color:#7A8296;">· {confidence:.0f}% confidence</span>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────
#  Live Occupancy Widget (real bookings + lot baseline — no fake sensors)
# ──────────────────────────────────────────────────────────────────
def live_occupancy_widget(meta, empty_spots, occupied_spots, capacity):
    pct = (occupied_spots / capacity) * 100
    active_now = meta.get("active_bookings_now", 0)
    baseline_pct = meta.get("baseline_utilization_pct", 0)
    updated = meta.get("last_updated", "")

    st.markdown(
        '<div class="glass-card" style="border-left:3px solid #39FF14 !important;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">'
        '<div style="font-size:0.92rem;font-weight:800;color:#39FF14;">'
        '<span class="live-dot"></span>🅿️ Live Occupancy'
        '</div>'
        f'<span class="badge badge-green">Updated {updated}</span>'
        '</div>'
        '<table style="width:100%;font-size:0.80rem;border-collapse:collapse;margin-bottom:12px;">'
        f'<tr><td style="padding:5px 0;color:#7A8296;width:55%;">Active bookings right now:</td>'
        f'<td style="color:#F0F0F0;font-weight:700;">{active_now}</td></tr>'
        f'<tr><td style="padding:5px 0;color:#7A8296;">Lot utilization baseline:</td>'
        f'<td style="color:#F0F0F0;font-weight:700;">{baseline_pct}%</td></tr>'
        f'<tr><td style="padding:5px 0;color:#7A8296;">Source:</td>'
        f'<td style="color:#F0F0F0;font-weight:700;">{meta.get("source","")}</td></tr>'
        '</table>'
        '<div style="padding:12px;background:rgba(57,255,20,0.04);border-radius:12px;border:1px solid rgba(57,255,20,0.14);">'
        '<div style="display:flex;justify-content:space-between;font-size:0.84rem;font-weight:700;margin-bottom:8px;">'
        f'<span style="color:#C8CDD8;">Total: {capacity} spaces</span>'
        f'<span style="color:#7A8296;">Occupancy: {pct:.1f}%</span>'
        '</div>'
        '<div style="background:rgba(0,0,0,0.35);width:100%;height:10px;border-radius:5px;overflow:hidden;">'
        f'<div style="background:linear-gradient(90deg,#22C55E,#39FF14);width:{pct:.1f}%;height:100%;border-radius:5px;"></div>'
        '</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px;font-size:0.82rem;text-align:center;">'
        '<div style="background:rgba(57,255,20,0.06);padding:8px;border-radius:10px;border:1px solid rgba(57,255,20,0.18);">'
        '<div style="color:#7A8296;font-size:0.68rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:2px;">Vacant</div>'
        f'<div style="font-weight:900;color:#39FF14;font-size:1.1rem;">{empty_spots}</div>'
        '</div>'
        '<div style="background:rgba(239,68,68,0.06);padding:8px;border-radius:10px;border:1px solid rgba(239,68,68,0.18);">'
        '<div style="color:#7A8296;font-size:0.68rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:2px;">Occupied</div>'
        f'<div style="font-weight:900;color:#FCA5A5;font-size:1.1rem;">{occupied_spots}</div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ──────────────────────────────────────────────────────────────────
#  Google Maps
# ──────────────────────────────────────────────────────────────────
def google_map_view(lots, center_lat=16.5062, center_lng=80.6480, height=440, selected_id=None):
    try:
        api_key = st.secrets["GOOGLE_MAPS_API_KEY"]
    except Exception:
        api_key = ""

    if api_key:
        markers_js = json.dumps([
            {"id": l["id"], "lat": l["lat"], "lng": l["lng"], "name": l["name"],
             "price": l.get("price_per_hour", 0), "rating": l.get("rating", 0)}
            for l in lots
        ])
        html = (
            f'<div id="map" style="width:100%;height:{height}px;border-radius:14px;overflow:hidden;"></div>'
            f'<script src="https://maps.googleapis.com/maps/api/js?key={api_key}"></script>'
            '<script>'
            f'function initAppMap(){{'
            f'const lots={markers_js};'
            f'const map=new google.maps.Map(document.getElementById("map"),{{center:{{lat:{center_lat},lng:{center_lng}}},zoom:13}});'
            'const iw=new google.maps.InfoWindow();'
            'lots.forEach(l=>{'
            'const m=new google.maps.Marker({position:{lat:l.lat,lng:l.lng},map,title:l.name});'
            'm.addListener("click",()=>{iw.setContent(`<div style="font-family:sans-serif;min-width:140px"><b>${l.name}</b><br/>⭐${l.rating} | ₹${l.price}/hr</div>`);iw.open(map,m);});'
            '});}'
            'initAppMap();'
            '</script>'
        )
        components.html(html, height=height + 10)
    else:
        st.info("💡 Add `GOOGLE_MAPS_API_KEY` in `.streamlit/secrets.toml` for a live map.")
        cols = st.columns(2)
        for i, lot in enumerate(lots):
            with cols[i % 2]:
                query = lot["address"].replace(" ", "+")
                st.markdown(
                    f'<iframe width="100%" height="210" style="border:0;border-radius:12px;" loading="lazy"'
                    f' src="https://www.google.com/maps?q={query}&output=embed"></iframe>'
                    f'<div style="text-align:center;font-size:0.80rem;color:#7A8296;margin-top:4px;">📍 {lot["name"]}</div>',
                    unsafe_allow_html=True
                )