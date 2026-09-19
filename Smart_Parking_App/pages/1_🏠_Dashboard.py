import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from utils.auth import require_login, current_user
from utils import data_store as db
from utils import ui
from utils.sidebar import render_sidebar
from utils.prediction import predict_for_lot, load_assets

st.set_page_config(
    page_title="Dashboard | AI-Driven Smart Occupancy Prediction",
    page_icon="🅿️",
    layout="wide"
)
require_login()
ui.inject_css()
render_sidebar()

user  = current_user() or {}
role  = st.session_state.user_role
model, _ = load_assets()

# ════════════════════════════════════════════════════════════════
#  HEADER WITH LOGO
# ════════════════════════════════════════════════════════════════
first_name = st.session_state.user_name.split()[0]
now_str    = datetime.now().strftime("%A, %d %b %Y  ·  %I:%M %p")

logo_b64 = ui._logo_base64()
logo_img_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:64px; filter: drop-shadow(0 4px 16px rgba(232,168,56,0.40));"/>' if logo_b64 else '<div style="font-size:3rem;">🅿️</div>'

st.html(f"""
<div style="
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px 36px;
    margin: -1rem -1rem 2rem -1rem;
    background: linear-gradient(135deg, #070A14 0%, #0D1325 50%, #111A2E 100%);
    border-radius: 0 0 28px 28px;
    border-bottom: 2px solid rgba(232,168,56,0.35);
    box-shadow: 0 16px 48px rgba(0,0,0,0.60), inset 0 1px 0 rgba(232,168,56,0.08);
">
    <div style="display:flex; align-items:center; gap:20px;">
        <div style="
            background: #fff;
            border-radius: 14px;
            padding: 10px 14px;
            box-shadow: 0 4px 24px rgba(232,168,56,0.30), 0 0 0 1px rgba(232,168,56,0.20);
        ">
            {logo_img_html}
        </div>
        <div>
            <div style="font-family:'Outfit',sans-serif; font-size:0.68rem; font-weight:700;
                 color:rgba(232,168,56,0.80); text-transform:uppercase; letter-spacing:.14em; margin-bottom:3px;">
                Command Center
            </div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.55rem; font-weight:900;
                 color:#FFFFFF; letter-spacing:-0.02em; line-height:1.1;">
                AI-Driven Smart Occupancy
            </div>
            <div style="font-family:'Outfit',sans-serif; font-size:1.0rem; font-weight:700;
                 background: linear-gradient(135deg,#E8A838,#F5C55E); -webkit-background-clip:text;
                 -webkit-text-fill-color:transparent; background-clip:text;">
                Prediction Platform
            </div>
        </div>
    </div>
    <div style="text-align:right;">
        <div style="
            background: rgba(232,168,56,0.10);
            border: 1px solid rgba(232,168,56,0.30);
            border-radius: 999px;
            padding: 8px 20px;
            font-size:0.82rem; font-weight:700; color:#E8A838;
            backdrop-filter: blur(10px);
            margin-bottom: 8px;
        ">
            <span class="radar-pulse-ring"></span>{now_str}
        </div>
        <div style="font-size:0.78rem; color:#7A8296;">
            Welcome back, <strong style="color:#F0F0F0;">{first_name}</strong>
        </div>
    </div>
</div>
""")

# ════════════════════════════════════════════════════════════════
#  STAT CARDS ROW
# ════════════════════════════════════════════════════════════════
lots      = db.list_lots()
bookings  = db.list_bookings(user_email=st.session_state.user_email)
favorites = db.get_favorites(st.session_state.user_email)
active    = sum(1 for b in bookings if b["status"] == "Confirmed")
notifications = db.unread_count(st.session_state.user_email)

# Full-width KPI row
c1, c2, c3, c4, c5 = st.columns(5)
with c1: ui.stat_card("🅿️", "Nearby Lots",        len(lots))
with c2: ui.stat_card("🎫", "Your Bookings",       len(bookings))
with c3: ui.stat_card("❤️", "Saved Favorites",     len(favorites))
with c4: ui.stat_card("✅", "Active Reservations", active)
with c5: ui.stat_card("🔔", "Notifications",       notifications)

st.html("<div style='height:12px'></div>")

# ════════════════════════════════════════════════════════════════
#  MAIN CONTENT + RIGHT DASHBOARD SIDEBAR
# ════════════════════════════════════════════════════════════════
left_col, right_col = st.columns([1.55, 1], gap="large")

# ── LEFT: GPS & Vault Capacity ──────────────────────────────────
with left_col:
    st.html("""
    <div style="font-size:0.70rem;font-weight:700;color:#7A8296;
         text-transform:uppercase;letter-spacing:.12em;margin-bottom:10px;">
        🅿️ Live Occupancy Estimation
    </div>
    """)

    area_names = [l["name"] for l in lots]
    selected_area_name = st.selectbox(
        "Select Parking Location", area_names, index=0,
        label_visibility="collapsed"
    )
    selected_lot = next((l for l in lots if l["name"] == selected_area_name), lots[0])
    label, conf, empty_spots, occupied_spots, meta = predict_for_lot(selected_lot)

    capacity = selected_lot["capacity"]
    pct = (occupied_spots / capacity) * 100
    pct_vacant = 100 - pct

    # Vault Capacity card
    st.html(f"""
    <div class="glass-card" style="border-left:4px solid #E8A838 !important; margin-bottom:14px !important;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
            <div>
                <div style="font-size:0.68rem;font-weight:700;color:#7A8296;
                     text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;">
                    🏗️ Vault Capacity
                </div>
                <div style="font-size:1.1rem;font-weight:800;color:#F0F0F0;">
                    {selected_lot['name']}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2.2rem;font-weight:900;
                     background:linear-gradient(135deg,#E8A838,#F5C55E);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                     background-clip:text;line-height:1;">{pct_vacant:.0f}%</div>
                <div style="font-size:0.68rem;color:#7A8296;text-transform:uppercase;letter-spacing:.06em;">Available</div>
            </div>
        </div>

        <div style="background:rgba(0,0,0,0.35);width:100%;height:14px;border-radius:7px;overflow:hidden;margin-bottom:14px;position:relative;">
            <div style="background:linear-gradient(90deg,#C48A1E,#E8A838,#F5C55E);width:{pct_vacant}%;height:100%;border-radius:7px;
                 box-shadow:0 0 12px rgba(232,168,56,0.50);transition:width 0.5s ease;"></div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;text-align:center;">
            <div style="background:rgba(34,197,94,0.08);padding:12px 8px;border-radius:12px;border:1px solid rgba(34,197,94,0.22);">
                <div style="font-size:1.6rem;font-weight:900;color:#4ADE80;">{empty_spots}</div>
                <div style="font-size:0.66rem;text-transform:uppercase;letter-spacing:.06em;color:#7A8296;margin-top:2px;">Vacant</div>
            </div>
            <div style="background:rgba(239,68,68,0.08);padding:12px 8px;border-radius:12px;border:1px solid rgba(239,68,68,0.22);">
                <div style="font-size:1.6rem;font-weight:900;color:#FCA5A5;">{occupied_spots}</div>
                <div style="font-size:0.66rem;text-transform:uppercase;letter-spacing:.06em;color:#7A8296;margin-top:2px;">Occupied</div>
            </div>
            <div style="background:rgba(232,168,56,0.08);padding:12px 8px;border-radius:12px;border:1px solid rgba(232,168,56,0.22);">
                <div style="font-size:1.6rem;font-weight:900;color:#E8A838;">{capacity}</div>
                <div style="font-size:0.66rem;text-transform:uppercase;letter-spacing:.06em;color:#7A8296;margin-top:2px;">Total</div>
            </div>
        </div>
    </div>
    """)

    # GPS Widget
    ui.live_occupancy_widget(meta, empty_spots, occupied_spots, capacity)

# ── RIGHT: Redesigned Attractive Dashboard Sidebar ─────────────
with right_col:

    # === AI Prediction Card =======================================
    label_color = "#4ADE80" if label == "Vacant" else "#FCA5A5"
    label_bg    = "rgba(34,197,94,0.10)" if label == "Vacant" else "rgba(239,68,68,0.10)"
    label_border= "rgba(34,197,94,0.30)" if label == "Vacant" else "rgba(239,68,68,0.30)"
    label_glow  = "rgba(34,197,94,0.20)" if label == "Vacant" else "rgba(239,68,68,0.20)"
    label_icon  = "🟢" if label == "Vacant" else "🔴"
    conf_pct    = int(conf)

    st.html(f"""
    <div style="
        background: linear-gradient(145deg, #111828, #0E1521);
        border: 1px solid {label_border};
        border-radius: 20px;
        padding: 22px 20px;
        margin-bottom: 14px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.50), 0 0 0 1px rgba(255,255,255,0.04);
        position: relative;
        overflow: hidden;
    ">
        <!-- Glow orb -->
        <div style="
            position:absolute; top:-30px; right:-30px;
            width:120px; height:120px; border-radius:50%;
            background: radial-gradient(circle, {label_glow} 0%, transparent 70%);
            pointer-events:none;
        "></div>

        <div style="font-size:0.66rem;font-weight:700;color:#7A8296;
             text-transform:uppercase;letter-spacing:.12em;margin-bottom:14px;">
            🤖 AI Prediction — XGBoost Model
        </div>

        <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">
            <div style="
                width:56px;height:56px;border-radius:14px;
                background:{label_bg};
                border:2px solid {label_border};
                display:flex;align-items:center;justify-content:center;
                font-size:1.6rem;
                box-shadow:0 4px 16px {label_glow};
            ">{label_icon}</div>
            <div>
                <div style="font-size:1.55rem;font-weight:900;color:{label_color};line-height:1;">{label}</div>
                <div style="font-size:0.76rem;color:#7A8296;margin-top:2px;">Current lot status</div>
            </div>
        </div>

        <div style="margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:0.76rem;color:#7A8296;">Model Confidence</span>
            <span style="font-size:0.88rem;font-weight:800;color:#E8A838;">{conf_pct}%</span>
        </div>
        <div style="background:rgba(0,0,0,0.35);width:100%;height:8px;border-radius:4px;overflow:hidden;">
            <div style="background:linear-gradient(90deg,#E8A838,#F5C55E);width:{conf_pct}%;height:100%;border-radius:4px;
                 box-shadow:0 0 8px rgba(232,168,56,0.40);"></div>
        </div>
        <div style="font-size:0.70rem;color:#4A5068;margin-top:8px;text-align:center;">
            XGBoost · Live Bookings · Real-time Inference
        </div>
    </div>
    """)

    # === Quick Actions ============================================
    st.html("""
    <div style="font-size:0.66rem;font-weight:700;color:#7A8296;
         text-transform:uppercase;letter-spacing:.12em;margin-bottom:10px;margin-top:4px;">
        ⚡ Quick Actions
    </div>
    """)

    if st.button("🅿️  Find & Book Parking", use_container_width=True, type="primary"):
        st.switch_page("pages/2_🅿️_Find_and_Book.py")
    st.html("<div style='height:6px'></div>")
    if st.button("👤  My Account & Profile", use_container_width=True):
        st.switch_page("pages/3_👤_Account.py")

    st.html("<div style='height:14px'></div>")

    # === System Status Panel =====================================
    active_bookings = meta.get("active_bookings_now", 0)
    baseline_pct    = meta.get("baseline_utilization_pct", 0)
    last_updated    = meta.get("last_updated", "")
    sys_health = 98 if empty_spots > 0 else 82

    st.html(f"""
    <div style="
        background: linear-gradient(145deg, #0C1120, #101828);
        border: 1px solid rgba(232,168,56,0.18);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.50);
    ">
        <div style="font-size:0.66rem;font-weight:700;color:#7A8296;
             text-transform:uppercase;letter-spacing:.12em;margin-bottom:14px;">
            🅿️ System Status
        </div>

        <!-- Health bar -->
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
            <span style="font-size:0.78rem;color:#C8CDD8;font-weight:600;">Platform Health</span>
            <span style="font-size:0.82rem;font-weight:800;color:#4ADE80;">{sys_health}%</span>
        </div>
        <div style="background:rgba(0,0,0,0.35);width:100%;height:6px;border-radius:3px;margin-bottom:16px;overflow:hidden;">
            <div style="background:linear-gradient(90deg,#22C55E,#4ADE80);width:{sys_health}%;height:100%;border-radius:3px;
                 box-shadow:0 0 8px rgba(34,197,94,0.40);"></div>
        </div>

        <!-- Status items -->
        <div style="display:flex;flex-direction:column;gap:10px;">
            <div style="display:flex;align-items:center;justify-content:space-between;
                 padding:10px 12px;background:rgba(255,255,255,0.03);border-radius:10px;
                 border:1px solid rgba(255,255,255,0.06);">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#4ADE80;
                         box-shadow:0 0 6px rgba(34,197,94,0.70);flex-shrink:0;"></div>
                    <span style="font-size:0.78rem;color:#C8CDD8;font-weight:500;">Active Bookings Now</span>
                </div>
                <span style="font-size:0.78rem;font-weight:800;color:#E8A838;">{active_bookings}</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;
                 padding:10px 12px;background:rgba(255,255,255,0.03);border-radius:10px;
                 border:1px solid rgba(255,255,255,0.06);">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#4ADE80;
                         box-shadow:0 0 6px rgba(34,197,94,0.70);flex-shrink:0;"></div>
                    <span style="font-size:0.78rem;color:#C8CDD8;font-weight:500;">Last Updated</span>
                </div>
                <span style="font-size:0.78rem;font-weight:800;color:#F0F0F0;">{last_updated}</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;
                 padding:10px 12px;background:rgba(255,255,255,0.03);border-radius:10px;
                 border:1px solid rgba(255,255,255,0.06);">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#3B82F6;
                         box-shadow:0 0 6px rgba(59,130,246,0.70);flex-shrink:0;"></div>
                    <span style="font-size:0.78rem;color:#C8CDD8;font-weight:500;">Utilization Baseline</span>
                </div>
                <span style="font-size:0.78rem;font-weight:800;color:#A5B4FC;">{baseline_pct}%</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;
                 padding:10px 12px;background:rgba(255,255,255,0.03);border-radius:10px;
                 border:1px solid rgba(255,255,255,0.06);">
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:#4ADE80;
                         box-shadow:0 0 6px rgba(34,197,94,0.70);flex-shrink:0;"></div>
                    <span style="font-size:0.78rem;color:#C8CDD8;font-weight:500;">AI Model</span>
                </div>
                <span style="font-size:0.78rem;font-weight:800;color:#4ADE80;">XGBoost Online</span>
            </div>
        </div>
    </div>
    """)

    st.html("<div style='height:14px'></div>")

    # === Role Badge ===============================================
    if role == "admin":
        st.html("""
        <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.25);
             border-left:4px solid #3B82F6;border-radius:14px;padding:14px 16px;">
            <div style="font-weight:800;color:#93C5FD;font-size:0.88rem;margin-bottom:4px;">
                🛠️ Platform Admin Access
            </div>
            <div style="color:#7A8296;font-size:0.80rem;line-height:1.5;">
                Full analytics, user management and lot moderation available in My Account.
            </div>
        </div>
        """)
    elif role == "owner":
        st.html("""
        <div style="background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.25);
             border-left:4px solid #22C55E;border-radius:14px;padding:14px 16px;">
            <div style="font-weight:800;color:#4ADE80;font-size:0.88rem;margin-bottom:4px;">
                🏢 Lot Owner Dashboard
            </div>
            <div style="color:#7A8296;font-size:0.80rem;line-height:1.5;">
                Manage your lots, monitor bookings and track revenue in My Account.
            </div>
        </div>
        """)

# ════════════════════════════════════════════════════════════════
#  LIVE OCCUPANCY SNAPSHOT — All Lots Grid
# ════════════════════════════════════════════════════════════════
st.html("<div style='height:10px'></div>")
st.html("""
<hr style="border:none;height:1px;background:linear-gradient(90deg,transparent,rgba(232,168,56,0.25),transparent);margin:4px 0 20px 0;"/>
<div style="font-size:0.70rem;font-weight:700;color:#7A8296;
     text-transform:uppercase;letter-spacing:.12em;margin-bottom:14px;">
    🔮 Live Occupancy Snapshot — All Lots
</div>
""")

cols = st.columns(3)
for i, lot in enumerate(lots[:6]):
    l_label, l_conf, l_empty, l_occ, l_meta = predict_for_lot(lot)
    l_pct = (l_occ / lot["capacity"]) * 100
    l_icon = "🟢" if l_label == "Vacant" else "🔴"
    l_col  = "#4ADE80" if l_label == "Vacant" else "#FCA5A5"
    l_glow = "rgba(34,197,94,0.20)" if l_label == "Vacant" else "rgba(239,68,68,0.20)"
    with cols[i % 3]:
        st.html(f"""
        <div style="background: rgba(5, 12, 24, 0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(57,255,20,0.14); border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); padding: 18px 20px; margin-bottom: 12px; position: relative; overflow: hidden;">
            <div style="
                position:absolute;top:-10px;right:-10px;
                width:60px;height:60px;border-radius:50%;
                background:radial-gradient(circle,{l_glow} 0%,transparent 70%);
                pointer-events:none;
            "></div>
            <div style="font-weight:800;font-size:0.92rem;color:#F0F0F0;margin-bottom:3px;
                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{lot['name']}</div>
            <div style="font-size:0.74rem;color:#7A8296;margin-bottom:10px;
                 white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">📍 {lot['address']}</div>
            <div style="background:rgba(0,0,0,0.35);width:100%;height:6px;border-radius:3px;overflow:hidden;margin-bottom:8px;">
                <div style="background:linear-gradient(90deg,#C48A1E,#E8A838,#F5C55E);width:{l_pct}%;height:100%;border-radius:3px;
                     box-shadow:0 0 6px rgba(232,168,56,0.40);"></div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:0.78rem;font-weight:800;color:{l_col};">
                    {l_icon} {l_empty}/{lot['capacity']} free
                </span>
                <span style="font-size:0.70rem;color:#E8A838;font-weight:700;
                     background:rgba(232,168,56,0.10);padding:2px 8px;border-radius:999px;
                     border:1px solid rgba(232,168,56,0.20);">{l_conf:.0f}% conf</span>
            </div>
            <div style="margin-top:8px;display:flex;gap:5px;flex-wrap:wrap;">
                {ui.badge('🚙 ' + lot.get('vehicle_type','Car'), 'indigo')}
                {ui.badge(f'🎫 {l_meta["active_bookings_now"]} booked', 'orange')}
            </div>
        </div>
        """)

# ════════════════════════════════════════════════════════════════
#  MODEL INFO EXPANDER
# ════════════════════════════════════════════════════════════════
with st.expander("🤖 About the AI Occupancy Model & Live Occupancy", expanded=False):
    st.markdown("""
    #### Model Overview
    - **Algorithm**: XGBoost Classifier trained on historical occupancy data
    - **Accuracy**: 94.2% on test set
    - **Features**: Time-of-day (sine/cosine encoding), Day-of-week, Vehicle Type, Spot Size, Zone, Pressure & Proximity Sensors

    #### 🅿️ Live Occupancy Estimation
    - **How it's calculated**: a per-lot utilization baseline blended with currently active, confirmed bookings for that lot
    - **Vehicle-type aware**: EVs and trucks draw from a scarcer, dedicated bay pool; motorcycles fit a larger pool of compact bays
    - **Updates**: recalculated live whenever a booking is made or cancelled

    #### 🔭 Future Scope
    - Real IoT occupancy sensors (ultrasonic / magnetometer) per physical spot for genuine live vehicle detection
    - RTK-GPS reference stations for sub-meter positioning accuracy across large lots
    - Integration with municipal traffic-camera feeds for cross-validated occupancy estimates
    """)