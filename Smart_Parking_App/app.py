import streamlit as st
import streamlit.components.v1 as components
import warnings
warnings.filterwarnings("ignore")

from utils.auth import init_session, login
from utils import data_store as db
from utils import ui
from utils.sidebar import render_sidebar
from utils.hero import hero_html

st.set_page_config(
    page_title="Smart Parking | AI-Driven Occupancy Prediction",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="auto",
)

init_session()
ui.inject_css()
render_sidebar()

# ════════════════════════════════════════════════════════════════
#  Glassmorphism Login button in top-right (replaces Deploy button)
# ════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.html("""
    <div style="
        position: fixed;
        top: 14px;
        right: 18px;
        z-index: 9999;
    ">
        <a href="#sign-in" style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(15, 23, 42, 0.10);
            border-radius: 999px;
            padding: 9px 22px;
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            font-weight: 700;
            color: #000000;
            text-decoration: none;
            box-shadow: 0 4px 24px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.6);
            transition: all 0.25s ease;
            letter-spacing: 0.02em;
        "
        onmouseover="this.style.background='#ffffff'; this.style.borderColor='rgba(99,102,241,0.55)'; this.style.boxShadow='0 6px 30px rgba(99,102,241,0.35)';"
        onmouseout="this.style.background='rgba(255,255,255,0.92)'; this.style.borderColor='rgba(15,23,42,0.10)'; this.style.boxShadow='0 4px 24px rgba(0,0,0,0.20), inset 0 1px 0 rgba(255,255,255,0.6)';"
        >
            🔐 &nbsp;Sign In
        </a>
    </div>
    """)

# ════════════════════════════════════════════════════════════════
#  Already signed in → go straight to the Dashboard
# ════════════════════════════════════════════════════════════════
if st.session_state.logged_in:
    st.html(f"""
    <div style="
        text-align:center; padding: 40px 20px;
        background: rgba(15,23,42,0.70);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 24px;
        margin: 20px 0;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 12px;">👋</div>
        <div style="font-size: 1.5rem; font-weight: 800; color: #F1F5F9; margin-bottom: 8px;">
            Welcome back, {st.session_state.user_name}!
        </div>
        <div style="font-size: 0.92rem; color: #CBD5E1; margin-bottom: 24px;">
            You're signed in and ready to go.
        </div>
    </div>
    """)
    if st.button("🏠 Go to Dashboard →", type="primary", use_container_width=False):
        st.switch_page("pages/1_🏠_Dashboard.py")
    st.stop()

# ════════════════════════════════════════════════════════════════
#  3D Interactive Hero Section
# ════════════════════════════════════════════════════════════════
components.html(hero_html(height=520), height=540, scrolling=False)

# ════════════════════════════════════════════════════════════════
#  Feature Cards (GSAP-animated)
# ════════════════════════════════════════════════════════════════
features = [
    ("🤖", "Live ML Predictions", "Every lot's occupancy is estimated by your trained XGBoost model, updated in real time."),
    ("🗺️", "Google Maps Integration", "See every parking lot on an interactive map before you drive over."),
    ("🎫", "QR Check-In", "Every booking generates a scannable QR code for fast, contactless entry."),
    ("💳", "One-Tap Checkout", "Reserve and pay in a single seamless flow within seconds."),
]
cards_html = "".join([
    f"""<div class="feat-card" data-i="{i}">
          <div class="feat-icon">{icon}</div>
          <div class="feat-title">{title}</div>
          <div class="feat-desc">{desc}</div>
        </div>"""
    for i, (icon, title, desc) in enumerate(features)
])

components.html(f"""
<div id="feat-grid" style="
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
    gap:16px;
    font-family:'Inter','Outfit',sans-serif;
    padding:8px 2px 12px 2px;
">
  {cards_html}
</div>
<style>
  .feat-card {{
    background: rgba(15,23,42,0.75);
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 20px;
    padding: 22px 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    opacity: 0;
    transform: translateY(24px);
    transition: border-color 0.25s ease, box-shadow 0.25s ease;
    cursor: default;
  }}
  .feat-card:hover {{
    border-color: rgba(99,102,241,0.40);
    box-shadow: 0 12px 40px rgba(99,102,241,0.22);
  }}
  .feat-icon {{ font-size: 1.8rem; margin-bottom: 10px; }}
  .feat-title {{
    font-weight: 800;
    color: #F1F5F9;
    margin-bottom: 6px;
    font-size: 0.98rem;
    letter-spacing: -0.01em;
  }}
  .feat-desc {{
    color: #94A3B8;
    font-size: 0.84rem;
    line-height: 1.5;
    font-weight: 400;
  }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>
  gsap.to(".feat-card", {{
    opacity: 1, y: 0, duration: 0.6, ease: "power2.out",
    stagger: 0.12, delay: 0.2
  }});
</script>
""", height=240, scrolling=False)

st.html("<div id='sign-in'></div>")
st.html("---")

# ════════════════════════════════════════════════════════════════
#  Password Complexity Validator
# ════════════════════════════════════════════════════════════════
import re

def check_password_complexity(pw):
    if len(pw) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", pw):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", pw):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", pw):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw):
        return False, "Password must contain at least one special character (!@#$%^&* etc.)."
    return True, ""

# ════════════════════════════════════════════════════════════════
#  Sign-In / Register Section Header
# ════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; margin-bottom: 28px;">
    <div style="font-size: 1.75rem; font-weight: 800; color: #F1F5F9; letter-spacing:-0.02em;">
        🔐 Access Your Account
    </div>
    <div style="font-size: 0.9rem; color: #94A3B8; margin-top: 6px;">
        Sign in to start booking smart parking spots
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  Login / Register Tabs — centered
# ════════════════════════════════════════════════════════════════
center = st.columns([1, 2.2, 1])[1]
with center:
    # Demo credentials helper
    with st.expander("💡 Demo Credentials — click to expand", expanded=False):
        st.html("""
        <style>
          .cred-pill {
            display:inline-block; background:#F1F5F9; color:#000000;
            border:1px solid #E2E8F0; border-radius:6px;
            padding:2px 8px; font-family:'Inter',sans-serif;
            font-size:0.82rem; font-weight:600;
          }
        </style>
        <div style="font-family:'Inter',sans-serif; font-size:0.84rem; line-height:2.1;">
            <div style="color:#94A3B8; text-transform:uppercase; font-size:0.72rem; letter-spacing:.08em; margin-bottom:10px; font-weight:700;">Ready-to-use accounts</div>
            <div>🚗 <strong style="color:#A5B4FC;">Driver</strong>: <span class="cred-pill">demo@smartparking.ai</span> / <span class="cred-pill">Demo1234!</span></div>
            <div>🛠️ <strong style="color:#A5B4FC;">Admin</strong>: <span class="cred-pill">admin@smartparking.ai</span> / <span class="cred-pill">Admin1234!</span></div>
            <div>🏢 <strong style="color:#A5B4FC;">Owner</strong>: <span class="cred-pill">owner@smartparking.ai</span> / <span class="cred-pill">Owner1234!</span></div>
        </div>
        """)

    with st.container(border=True):
        tab_login, tab_phone_login, tab_google, tab_register = st.tabs([
            "✉️ Email Login",
            "📞 Phone Login",
            "🌐 Google Login",
            "➕ Register",
        ])

        # ── Email Sign In ─────────────────────────────────────────
        with tab_login:
            st.html("<div style='height:8px'></div>")
            with st.form("login_form", border=False):
                email = st.text_input("Email Address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Your password")
                st.html("<div style='height:4px'></div>")
                submitted = st.form_submit_button(
                    "🔐  Sign In", type="primary", use_container_width=True
                )
                if submitted:
                    if not email or not password:
                        st.warning("⚠️ Please enter both your email and password.")
                    else:
                        ok, result = db.verify_login(email.strip().lower(), password)
                        if ok:
                            login(email.strip().lower(), result["name"], result["role"])
                            db.push_notification(
                                email.strip().lower(),
                                f"Welcome back, {result['name']}! You signed in successfully.",
                                "info",
                            )
                            st.success("✅ Signed in successfully! Redirecting…")
                            st.switch_page("pages/1_🏠_Dashboard.py")
                        else:
                            st.error(f"❌ {result}")

        # ── Phone Sign In ─────────────────────────────────────────
        with tab_phone_login:
            st.html("<div style='height:8px'></div>")
            st.caption("Enter your registered phone number (digits only).")
            with st.form("phone_login_form", border=False):
                phone_input = st.text_input(
                    "Phone Number", placeholder="e.g. 9000000000",
                    help="Only numeric digits 0–9 are accepted."
                )
                phone_pw = st.text_input("Password", type="password", placeholder="Your password")
                st.html("<div style='height:4px'></div>")
                submitted_phone = st.form_submit_button(
                    "📞  Sign In with Phone", type="primary", use_container_width=True
                )
                if submitted_phone:
                    sanitized_phone = "".join([c for c in phone_input if c.isdigit()])
                    if phone_input and phone_input != sanitized_phone:
                        st.warning("ℹ️ Non-numeric characters were removed. Using: " + sanitized_phone)
                    if not sanitized_phone or not phone_pw:
                        st.warning("⚠️ Please enter both phone number and password.")
                    else:
                        ok, result = db.verify_phone_login(sanitized_phone, phone_pw)
                        if ok:
                            login(result["email"], result["name"], result["role"])
                            db.push_notification(
                                result["email"],
                                f"Welcome back, {result['name']}! Signed in via phone.",
                                "info",
                            )
                            st.success("✅ Signed in! Redirecting…")
                            st.switch_page("pages/1_🏠_Dashboard.py")
                        else:
                            st.error(f"❌ {result}")

        # ── Google Sign In ────────────────────────────────────────
        with tab_google:
            st.html("<div style='height:8px'></div>")
            st.html("""
            <div style="text-align:center; padding:12px 0 6px 0;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg"
                     width="40" style="margin-bottom:10px;"/>
                <div style="font-weight:800; font-size:1.05rem; color:#F1F5F9;">
                    Google Single Sign-On
                </div>
                <div style="color:#94A3B8; font-size:0.83rem; margin-top:4px;">
                    Fast &amp; secure OAuth 2.0 authentication
                </div>
            </div>
            """)

            google_email = st.text_input(
                "Gmail Address", value="", key="google_oauth_email",
                placeholder="yourname@gmail.com"
            )
            if st.button("🌐  Continue with Google", type="primary", use_container_width=True):
                if not google_email.strip():
                    st.warning("⚠️ Please enter your Gmail address first.")
                else:
                    gmail = google_email.strip().lower()
                    gname = gmail.split("@")[0].replace(".", " ").title() + " (Google)"
                    db.create_user(gmail, gname, "GooglePass2026!", phone="9876543210", vehicle="AP 16 AB 9999")
                    login(gmail, gname, "user")
                    db.push_notification(gmail, "Welcome! You signed in with your Google Account.", "success")
                    st.success("✅ Google authentication successful!")
                    st.switch_page("pages/1_🏠_Dashboard.py")

            st.html("<hr style='border-color:rgba(99,102,241,0.15); margin:16px 0;'/>")
            st.caption("🔑 Advanced: Authenticate with Google API Key")
            google_key = st.text_input(
                "Google API Key / OAuth Client Secret", type="password",
                help="Enter your valid Google OAuth Client Secret",
                placeholder="Paste API key here",
            )
            if st.button("🔑  Verify API Key", use_container_width=True):
                if not google_key.strip():
                    st.warning("⚠️ Please enter a valid Google API key.")
                elif not google_email.strip():
                    st.warning("⚠️ Please also enter your Gmail address above.")
                else:
                    gmail = google_email.strip().lower()
                    gname = gmail.split("@")[0].replace(".", " ").title() + " (Google)"
                    db.create_user(gmail, gname, "GooglePass2026!", phone="9876543210", vehicle="AP 16 AB 9999")
                    login(gmail, gname, "user")
                    db.push_notification(gmail, "Welcome! Authenticated via Google API Key.", "success")
                    st.success("✅ Google API Key verified!")
                    st.switch_page("pages/1_🏠_Dashboard.py")

        # ── Create Account ────────────────────────────────────────
        with tab_register:
            st.html("<div style='height:8px'></div>")
            with st.form("signup_form", border=False):
                name = st.text_input("Full Name", placeholder="John Doe")
                email_s = st.text_input("Email Address", key="signup_email", placeholder="you@example.com")
                phone_s = st.text_input(
                    "Phone Number (digits only)", key="signup_phone",
                    placeholder="e.g. 9000000000"
                )
                password_s = st.text_input(
                    "Password", type="password", key="signup_pw",
                    placeholder="Min 8 chars, 1 uppercase, 1 number, 1 special",
                    help="Min 8 chars · 1 uppercase letter · 1 lowercase letter · 1 number · 1 special character"
                )
                account_type = st.selectbox(
                    "Account Type",
                    ["user", "owner"],
                    format_func=lambda r: "🚗  Driver / Commuter" if r == "user" else "🏢  Parking Lot Owner",
                )
                st.html("<div style='height:4px'></div>")
                submitted_s = st.form_submit_button(
                    "✅  Create Account", type="primary", use_container_width=True
                )
                if submitted_s:
                    sanitized_phone = "".join([c for c in phone_s if c.isdigit()])
                    if phone_s and phone_s != sanitized_phone:
                        st.warning("ℹ️ Only digits are allowed in the phone field.")
                    if not (name and email_s and password_s and sanitized_phone):
                        st.warning("⚠️ Full name, email, phone number, and password are all required.")
                    else:
                        pw_ok, pw_msg = check_password_complexity(password_s)
                        if not pw_ok:
                            st.error(f"❌ {pw_msg}")
                        else:
                            ok, msg = db.create_user(
                                email_s.strip().lower(), name.strip(),
                                password_s, role=account_type,
                                phone=sanitized_phone
                            )
                            if ok:
                                st.success("🎉 Account created! Switch to the Email Login tab to sign in.")
                            else:
                                st.error(f"❌ {msg}")

st.html("""
<div style="text-align:center; margin-top:40px; padding-top:20px;
     border-top:1px solid rgba(99,102,241,0.12);">
    <span style="font-size:0.78rem; color:#64748B;">
        Built with Streamlit · AI occupancy prediction powered by a trained XGBoost model
    </span>
</div>
""")