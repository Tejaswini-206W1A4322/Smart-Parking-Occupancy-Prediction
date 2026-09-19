import streamlit as st
from utils import data_store as db
from utils.auth import logout
from utils.ui import _logo_base64

ROLE_LABEL = {"user": "Driver", "admin": "Platform Admin", "owner": "Lot Owner"}
ROLE_ICON  = {"user": "🚗",    "admin": "🛠️",             "owner": "🏢"}
ROLE_COLOR = {"user": "#39FF14", "admin": "#3B82F6",       "owner": "#22C55E"}


def render_sidebar():
    with st.sidebar:
        # ── Brand / Logo Header ──────────────────────────────────
        logo_b64 = _logo_base64()
        logo_html = (
            f'<img src="data:image/png;base64,{logo_b64}" style="height:40px;display:block;"/>'
            if logo_b64 else '<div style="font-size:2rem;">🅿️</div>'
        )

        st.html(f"""
        <div style="padding:20px 16px 14px;border-bottom:1px solid rgba(57,255,20,0.15);margin-bottom:4px;">
            <div style="background:#fff;border-radius:10px;padding:6px 10px;
                 display:inline-block;margin-bottom:10px;
                 box-shadow:0 0 20px rgba(57,255,20,0.25);">
                {logo_html}
            </div>
            <div style="font-family:'Outfit',sans-serif;font-size:0.88rem;font-weight:800;
                 color:#F0F0F0;line-height:1.25;">AI-Driven Smart<br/>Occupancy</div>
            <div style="font-size:0.60rem;font-weight:700;color:#39FF14;
                 text-transform:uppercase;letter-spacing:.12em;margin-top:3px;">
                Smart Parking Engine
            </div>
        </div>
        """)

        # ── NAVIGATION label ──────────────────────────────────────
        st.html("""
        <div style="font-size:0.58rem;font-weight:800;color:rgba(148,163,184,0.50);
             text-transform:uppercase;letter-spacing:.20em;
             padding:14px 16px 6px;">NAVIGATION</div>
        """)

        # ── NAV CSS — style page_link & hide raw button labels ────
        st.html("""
        <style>
        /* Style page_link nav items */
        section[data-testid="stSidebar"] [data-testid="stPageLink"] {
            margin: 2px 6px !important;
            border-radius: 12px !important;
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
            display: flex !important;
            align-items: center !important;
            padding: 11px 16px !important;
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
        }
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
            background: rgba(57,255,20,0.09) !important;
            border-color: rgba(57,255,20,0.22) !important;
            color: #39FF14 !important;
        }
        /* Active page link gets highlight */
        section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
            background: #39FF14 !important;
            color: #020508 !important;
            font-weight: 900 !important;
            box-shadow: 0 0 18px rgba(57,255,20,0.50) !important;
            border-color: transparent !important;
        }
        /* Collapse all raw st.button text in sidebar except logout */
        section[data-testid="stSidebar"] .stButton > button:not(:last-child) {
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            overflow: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
            font-size: 0 !important;
            line-height: 0 !important;
            display: block !important;
            visibility: hidden !important;
        }
        </style>
        """)

        # ── Navigation items (only real, functional pages) ────────
        st.page_link("pages/1_🏠_Dashboard.py",     label="⊞  Dashboard")
        st.page_link("pages/2_🅿️_Find_and_Book.py", label="🔍  Find & Book Parking")
        st.page_link("pages/3_👤_Account.py",        label="👤  My Account")

        # ── User / Guest State ───────────────────────────────────
        if st.session_state.get("logged_in"):
            role      = st.session_state.get("user_role", "user")
            unread    = db.unread_count(st.session_state.user_email)
            bell      = f"🔔 {unread} new alerts" if unread else "🔔 No new alerts"
            role_col  = ROLE_COLOR.get(role, "#39FF14")

            st.html("<div style='height:8px'></div>")
            st.html(f"""
            <div style="background:rgba(57,255,20,0.05);
                 border:1px solid rgba(57,255,20,0.15);
                 border-left:3px solid {role_col};
                 border-radius:12px;padding:12px 14px;margin:8px;">
                <div style="font-size:0.86rem;font-weight:800;color:#F0F0F0;margin-bottom:2px;">
                    {ROLE_ICON.get(role,'👤')} {st.session_state.user_name}
                </div>
                <div style="font-size:0.60rem;color:{role_col};font-weight:700;
                     text-transform:uppercase;letter-spacing:.10em;margin-top:2px;">
                    {ROLE_LABEL.get(role, role)}
                </div>
                <div style="font-size:0.70rem;color:#94A3B8;margin-top:4px;">{bell}</div>
            </div>
            """)

            st.html("<div style='height:8px'></div>")
            if st.button("🚪  Log Out", use_container_width=True, key="logout_sidebar"):
                logout()
                st.switch_page("app.py")
        else:
            st.html("<div style='height:8px'></div>")
            st.html("""
            <div style="padding:14px;background:rgba(57,255,20,0.04);
                 border:1px solid rgba(57,255,20,0.15);border-radius:14px;
                 text-align:center;margin:8px;">
                <div style="font-size:1.3rem;margin-bottom:6px;">🔐</div>
                <div style="font-size:0.84rem;font-weight:700;color:#E8E8E8;margin-bottom:4px;">
                    Sign in to access
                </div>
                <div style="font-size:0.72rem;color:#7A8296;line-height:1.5;">
                    Dashboard, bookings &amp;<br/>live parking map.
                </div>
            </div>
            """)

        st.html("""
        <hr style="border-color:rgba(57,255,20,0.10);margin:14px 0 6px 0;"/>
        <div style="font-size:0.64rem;color:#4A5068;text-align:center;padding-bottom:6px;">
            © 2026 Smart Parking · AI-Powered Platform
        </div>
        """)
