import pandas as pd
import streamlit as st
from utils.auth import require_login, current_user
from utils import data_store as db
from utils import ui
from utils.sidebar import render_sidebar
from utils.qr_utils import generate_booking_qr
from utils.payment import refund_payment
from utils.prediction import predict_for_lot

st.set_page_config(page_title="My Account | Smart Parking", page_icon="👤", layout="wide")
require_login()
ui.inject_css()
render_sidebar()

role = st.session_state.user_role
user = current_user() or {}


# ════════════════════════════════════════════════════════════════
#  DRIVER — Profile / Bookings / Favorites / Notifications
# ════════════════════════════════════════════════════════════════
def render_driver_account():
    ui.top_header("👤 My Account", "Profile, bookings, favorites, and notifications — all in one place.")

    tab_profile, tab_bookings, tab_favs, tab_notifs = st.tabs(
        ["👤 Profile", "🎫 My Bookings", "❤️ Favorites", "🔔 Notifications"]
    )

    # ── Profile ────────────────────────────────────────────────
    with tab_profile:
        bookings_all = db.list_bookings(user_email=st.session_state.user_email)
        favorites_all = db.get_favorites(st.session_state.user_email)
        total_spent = sum(b["amount"] for b in bookings_all if b["status"] in ("Confirmed", "Completed"))

        left, right = st.columns([1, 1.4], gap="large")
        with left:
            st.html(f"""
            <div class="glass-card" style="text-align:center;">
                <div style="font-size:3rem;">🧑‍💼</div>
                <h3>{user.get('name','—')}</h3>
                <span class="muted">{st.session_state.user_email}</span><br/>
                {ui.badge('Driver', 'indigo')}
            </div>
            """)
            c1, c2, c3 = st.columns(3)
            with c1: ui.stat_card("🎫", "Bookings", len(bookings_all))
            with c2: ui.stat_card("❤️", "Favorites", len(favorites_all))
            with c3: ui.stat_card("💰", "Total Spent", f"₹{total_spent:.0f}")

        with right:
            with st.container(border=True):
                st.html("#### ✏️ Edit Details")
                with st.form("profile_form", border=False):
                    name = st.text_input("Full Name", value=user.get("name", ""))
                    phone_input = st.text_input("Phone Number (digits only)", value=user.get("phone", ""))
                    vehicle = st.text_input("Default Vehicle Number", value=user.get("vehicle", ""))
                    save = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
                if save:
                    # Sanitize the phone number: allow only numbers
                    sanitized_phone = "".join([c for c in phone_input if c.isdigit()])
                    if not name.strip():
                        st.warning("Full Name is required.")
                    elif not phone_input.strip() or len(sanitized_phone) == 0:
                        st.warning("Please enter a valid phone number containing only numeric digits.")
                    else:
                        if phone_input != sanitized_phone:
                            st.info(f"Non-digits removed. Phone number saved as: {sanitized_phone}")
                        db.update_profile(st.session_state.user_email, name=name.strip(), phone=sanitized_phone, vehicle=vehicle.strip())
                        st.session_state.user_name = name
                        st.success("Profile updated.")
                        st.rerun()

            with st.container(border=True):
                st.markdown("#### 🔔 Preferences")
                st.toggle("Email me booking confirmations", value=True, key="pref_email")
                st.toggle("SMS reminders before parking expiry", value=True, key="pref_sms")
                st.toggle("Marketing updates & offers", value=False, key="pref_marketing")

    # ── Bookings ───────────────────────────────────────────────
    with tab_bookings:
        bookings = db.list_bookings(user_email=st.session_state.user_email)
        if not bookings:
            st.info("You haven't made any bookings yet.")
            if st.button("🅿️ Find Parking"):
                st.switch_page("pages/2_🅿️_Find_and_Book.py")
        else:
            status_filter = st.radio("Filter", ["All", "Confirmed", "Cancelled", "Completed"], horizontal=True)
            shown = bookings if status_filter == "All" else [b for b in bookings if b["status"] == status_filter]

            for b in shown:
                lot = db.get_lot(b["lot_id"]) or {}
                kind = {"Confirmed": "badge-green", "Cancelled": "badge-red",
                        "Completed": "badge-indigo"}.get(b["status"], "badge-gray")
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2.2, 1.3, 1])
                    with c1:
                        st.markdown(f"**{b['lot_name']}**  \n📍 {lot.get('address','—')}")
                        st.markdown(f"🕐 {b['slot_time']} · ⏱️ {b['duration_hrs']}h · "
                                    f"🚙 {b.get('vehicle_type','—')} · {b.get('vehicle_number','—')}")
                        st.markdown(f"Booking ID: `{b['id']}`  ·  {ui.badge(b['status'], kind)}", unsafe_allow_html=True)
                    with c2:
                        st.html(f"**₹{b['amount']:.2f}**")
                        st.caption(f"via {b.get('payment_method','—')}")
                        st.caption(f"Paid: `{b.get('razorpay_payment_id','—')}`")
                    with c3:
                        qr_bytes = generate_booking_qr(b)
                        st.image(qr_bytes, width=110)
                        if b["status"] == "Confirmed":
                            if st.button("Cancel", key=f"cancel_{b['id']}", use_container_width=True):
                                db.update_booking_status(b["id"], "Cancelled")
                                refund_payment(b.get("razorpay_payment_id", ""), b["amount"])
                                db.push_notification(
                                    st.session_state.user_email,
                                    f"Booking {b['id']} cancelled. Refund of ₹{b['amount']:.2f} initiated.",
                                    "warning")
                                st.rerun()

    # ── Favorites ──────────────────────────────────────────────
    with tab_favs:
        fav_ids = db.get_favorites(st.session_state.user_email)
        lots = [l for l in db.list_lots() if l["id"] in fav_ids]
        if not lots:
            st.info("No favorites yet — tap the ❤️ icon on any lot to save it here.")
            if st.button("🅿️ Browse Parking Lots"):
                st.switch_page("pages/2_🅿️_Find_and_Book.py")
        else:
            cols = st.columns(3)
            for i, lot in enumerate(lots):
                label, conf, empty_spots, occupied_spots, meta = predict_for_lot(lot)
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="lot-card">
                        <img src="{lot.get('image','')}" onerror="this.style.display='none'"/>
                        <div class="lot-card-body">
                            <div class="lot-card-title">{lot['name']}</div>
                            <div class="lot-card-sub">📍 {lot['address']}</div>
                            <div class="lot-tags">
                                {ui.badge(f"⭐ {lot.get('rating',0):.1f}", "orange")}
                                {ui.badge('🚙 ' + lot.get('vehicle_type','Car'), "indigo")}
                                {ui.badge(f"🎫 {meta['active_bookings_now']} booked", "green")}
                            </div>
                            <span class="price-tag">₹{lot.get('price_per_hour',0)}/hr</span>
                            <div style="font-size:0.82rem; font-weight:800; color:var(--success); margin-top:6px;">
                                🟢 {empty_spots} vacant spots (live)
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    ui.prediction_badge(label, conf)
                    st.write("")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("View Details", key=f"vdet_{lot['id']}", use_container_width=True):
                            st.session_state.selected_lot_id = lot["id"]
                            st.switch_page("pages/2_🅿️_Find_and_Book.py")
                    with b2:
                        if st.button("💔 Remove", key=f"rm_{lot['id']}", use_container_width=True):
                            db.toggle_favorite(st.session_state.user_email, lot["id"])
                            st.rerun()

    # ── Notifications ──────────────────────────────────────────
    with tab_notifs:
        notes = db.list_notifications(st.session_state.user_email)
        top1, top2 = st.columns([4, 1])
        with top2:
            if st.button("Mark all read", use_container_width=True):
                db.mark_all_read(st.session_state.user_email)
                st.rerun()
        if not notes:
            st.info("You're all caught up — no notifications yet.")
        else:
            icon_map = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "🔴"}
            for n in notes:
                cls = "notif-item notif-unread" if not n["read"] else "notif-item"
                icon = icon_map.get(n.get("kind", "info"), "🔔")
                ts = n["time"].replace("T", " ")[:16]
                st.html(f"""
                <div class="{cls}">{icon} {n['message']}<div class="notif-time">{ts}</div></div>
                """)


# ════════════════════════════════════════════════════════════════
#  ADMIN — Platform-wide management
# ════════════════════════════════════════════════════════════════
def render_admin_account():
    ui.top_header("🛠️ Admin Dashboard", "Platform-wide analytics, users, and parking-lot moderation.")

    lots = db.list_lots()
    bookings = db.list_bookings()
    users = db.load_db()["users"]
    revenue = sum(b["amount"] for b in bookings if b["status"] in ("Confirmed", "Completed"))

    c1, c2, c3, c4 = st.columns(4)
    with c1: ui.stat_card("🅿️", "Total Lots", len(lots))
    with c2: ui.stat_card("👥", "Total Users", len(users))
    with c3: ui.stat_card("🎫", "Total Bookings", len(bookings))
    with c4: ui.stat_card("💰", "Gross Revenue", f"₹{revenue:,.0f}")

    tab_overview, tab_lots, tab_bookings, tab_users = st.tabs(
        ["📊 Overview", "🅿️ Lots", "🎫 Bookings", "👥 Users"]
    )

    with tab_overview:
        if bookings:
            df = pd.DataFrame(bookings)
            st.html("#### Revenue by Parking Lot")
            st.bar_chart(df.groupby("lot_name")["amount"].sum().sort_values(ascending=False))
            st.markdown("#### Bookings by Status")
            st.bar_chart(df["status"].value_counts())
            if "vehicle_type" in df.columns:
                st.markdown("#### Bookings by Vehicle Type")
                st.bar_chart(df["vehicle_type"].value_counts())
        else:
            st.info("No bookings yet — charts will populate once drivers start booking.")

    with tab_lots:
        for lot in lots:
            with st.expander(f"{lot['name']} · {lot['address']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Capacity:** {lot['capacity']}")
                    st.write(f"**Price/hr:** ₹{lot['price_per_hour']}")
                    st.write(f"**Rating:** {lot['rating']}")
                    st.write(f"**Vehicle Type:** {lot.get('vehicle_type','—')}")
                    st.write(f"**Owner:** {lot.get('owner_email','—')}")
                with c2:
                    new_price = st.number_input("Update price/hr (₹)", value=float(lot["price_per_hour"]),
                                                 key=f"price_{lot['id']}")
                    if st.button("Save Price", key=f"save_{lot['id']}"):
                        db.update_lot(lot["id"], price_per_hour=new_price)
                        st.success("Price updated.")
                        st.rerun()

    with tab_bookings:
        if bookings:
            df = pd.DataFrame(bookings)[["id", "user_email", "lot_name", "slot_time", "duration_hrs",
                                          "vehicle_type", "amount", "status", "payment_method"]]
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("No bookings recorded yet.")

    with tab_users:
        rows = [{"Email": e, "Name": u["name"], "Role": u["role"], "Phone": u.get("phone", "—")}
                for e, u in users.items()]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


# ════════════════════════════════════════════════════════════════
#  OWNER — Per-owner lot & booking management
# ════════════════════════════════════════════════════════════════
def render_owner_account():
    ui.top_header("🏢 Owner Dashboard", "Manage your parking lots, monitor bookings, and track revenue.")

    owner_email = st.session_state.user_email
    my_lots = db.list_lots(owner_email=owner_email)
    my_bookings = db.list_bookings(owner_email=owner_email)
    revenue = sum(b["amount"] for b in my_bookings if b["status"] in ("Confirmed", "Completed"))

    c1, c2, c3 = st.columns(3)
    with c1: ui.stat_card("🅿️", "My Lots", len(my_lots))
    with c2: ui.stat_card("🎫", "Bookings Received", len(my_bookings))
    with c3: ui.stat_card("💰", "My Revenue", f"₹{revenue:,.0f}")

    tab_lots, tab_bookings, tab_add = st.tabs(["🅿️ My Lots", "🎫 Bookings", "➕ Add New Lot"])

    with tab_lots:
        if not my_lots:
            st.info("You don't have any parking lots yet — add one in the **Add New Lot** tab.")
        for lot in my_lots:
            label, conf, empty_spots, occupied_spots, meta = predict_for_lot(lot)
            st.markdown(f"""
            <div class="glass-card">
                <b>{lot['name']}</b> · {ui.badge(lot.get('zone','—'),'gray')}<br/>
                <span class="muted">📍 {lot['address']}</span><br/><br/>
                {ui.badge(f"Capacity {lot['capacity']}", "indigo")}
                {ui.badge(f"₹{lot['price_per_hour']}/hr", "indigo")}
                {ui.badge(f"⭐ {lot['rating']}", "orange")}
                {ui.badge('🚙 ' + lot.get('vehicle_type','Car'), "indigo")}
                {ui.badge(f"🎫 {meta['active_bookings_now']} active bookings", "green")}
                <div style="font-size:0.9rem; font-weight:800; color:var(--success); margin-top:8px;">
                    🟢 {empty_spots} vacant spots out of {lot['capacity']} available slots
                </div>
            </div>
            """, unsafe_allow_html=True)
            ui.prediction_badge(label, conf)

    with tab_bookings:
        if my_bookings:
            df = pd.DataFrame(my_bookings)[["id", "user_email", "lot_name", "slot_time", "duration_hrs",
                                             "vehicle_type", "amount", "status"]]
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.info("No bookings received yet for your lots.")

    with tab_add:
        st.markdown("#### Add a New Parking Lot")
        with st.form("add_lot_form"):
            name = st.text_input("Lot Name")
            address = st.text_input("Address")
            c1, c2 = st.columns(2)
            lat = c1.number_input("Latitude", value=16.5062, format="%.4f")
            lng = c2.number_input("Longitude", value=80.6480, format="%.4f")
            c3, c4 = st.columns(2)
            capacity = c3.number_input("Capacity", min_value=1, value=100)
            price = c4.number_input("Price per hour (₹)", min_value=1, value=25)
            zone = st.selectbox("Zone", ["Zone A", "Zone B", "Zone C", "Zone D"])
            spot_size = st.selectbox("Spot Size", ["Standard", "Compact", "Oversized"])
            vehicle_type = st.selectbox("Primary Vehicle Type", ["Car", "Motorcycle", "Electric Vehicle", "Truck"])
            amenities = st.multiselect("Amenities", ["CCTV", "EV Charging", "Covered", "Security Guard",
                                                       "24x7 Open", "Two-Wheeler Bay", "Valet", "Open Air"])
            image_url = st.text_input(
                "Image URL (optional)",
                value="https://images.unsplash.com/photo-1573348722427-f1d6819fdf98?q=80&w=600&auto=format&fit=crop")
            submitted = st.form_submit_button("➕ Add Lot", type="primary", use_container_width=True)

        if submitted:
            if not (name and address):
                st.warning("Lot name and address are required.")
            else:
                lot_id = db.add_lot({
                    "name": name, "address": address, "lat": lat, "lng": lng,
                    "capacity": capacity, "price_per_hour": price, "rating": 4.0,
                    "zone": zone, "spot_size": spot_size, "vehicle_type": vehicle_type,
                    "user_type": "Visitor", "availability_bias": 0.5,
                    "amenities": amenities, "owner_email": owner_email, "image": image_url,
                })
                st.success(f"Lot added! (id: {lot_id})")
                st.rerun()


# ── Router ──────────────────────────────────────────────────────
if role == "admin":
    render_admin_account()
elif role == "owner":
    render_owner_account()
else:
    render_driver_account()