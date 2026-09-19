import streamlit as st
from datetime import datetime, timedelta
from utils.auth import require_login
from utils import data_store as db
from utils import ui
from utils.sidebar import render_sidebar
from utils.prediction import predict_for_lot
from utils.payment import create_order, capture_payment
from utils.qr_utils import generate_booking_qr

st.set_page_config(page_title="Find & Book Parking | Smart Parking", page_icon="🅿️", layout="wide")
require_login()
ui.inject_css()
render_sidebar()

VEHICLE_TYPES = ["Car", "Motorcycle", "Electric Vehicle", "Truck"]

# ── Keep the booking flow scoped to whichever lot is currently open.
#    Fixes: navigating to a different lot (or back to this page) no longer
#    inherits a stale "Confirmed" screen from a previous, unrelated booking.
lot_id = st.session_state.get("selected_lot_id")
if st.session_state.get("booking_step_lot_id") != lot_id:
    st.session_state.booking_step = "form"
    st.session_state.booking_step_lot_id = lot_id


# ════════════════════════════════════════════════════════════════
#  BROWSE VIEW — search, filters, map, lot cards
# ════════════════════════════════════════════════════════════════
def render_browse():
    ui.top_header("🅿️ Find & Book Parking", "Search nearby lots, check live availability, and reserve a spot.")

    lots = db.list_lots()
    favorites = set(db.get_favorites(st.session_state.user_email))

    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
    query = f1.text_input("🔎 Search by name or address", placeholder="e.g. Benz Circle, Railway Station...")
    zone_filter = f2.selectbox("Zone", ["All", "Zone A", "Zone B", "Zone C", "Zone D"])
    vehicle_filter = f3.selectbox("Vehicle Type", ["All"] + VEHICLE_TYPES)
    max_price = f4.slider("Max ₹/hr", 10, 60, 60, step=5)

    filtered = lots
    if query:
        q = query.lower()
        filtered = [l for l in filtered if q in l["name"].lower() or q in l["address"].lower()]
    if zone_filter != "All":
        filtered = [l for l in filtered if l.get("zone") == zone_filter]
    filtered = [l for l in filtered if l.get("price_per_hour", 0) <= max_price]

    st.html(f"**{len(filtered)}** parking lots found")

    with st.expander("🗺️ Map View", expanded=True):
        ui.google_map_view(filtered)

    st.markdown("---")

    cols = st.columns(3)
    for i, lot in enumerate(filtered):
        # If a vehicle type is chosen, run the prediction FOR that vehicle
        # type — the model was trained on this exact categorical feature.
        pred_lot = dict(lot)
        if vehicle_filter != "All":
            pred_lot["vehicle_type"] = vehicle_filter
        label, conf, empty_spots, occupied_spots, meta = predict_for_lot(pred_lot)
        is_fav = lot["id"] in favorites

        with cols[i % 3]:
            st.markdown(f"""
            <div class="lot-card">
                <img src="{lot.get('image','')}" onerror="this.style.display='none'"/>
                <div class="lot-card-body">
                    <div class="lot-card-title">{lot['name']}</div>
                    <div class="lot-card-sub">📍 {lot['address']}</div>
                    <div class="lot-tags">
                        {ui.badge(f"⭐ {lot.get('rating',0):.1f}", "orange")}
                        {ui.badge(lot.get('zone','—'), "gray")}
                        {ui.badge('🚙 ' + pred_lot.get('vehicle_type','Car'), "indigo")}
                        {ui.badge(f"🎫 {meta['active_bookings_now']} booked", "green")}
                    </div>
                    <span class="price-tag">₹{lot.get('price_per_hour',0)}/hr</span>
                    <span class="muted"> · {lot.get('capacity')} capacity</span>
                    <div style="font-size:0.85rem; font-weight:800; color:var(--success); margin:6px 0 0 0;">
                        🟢 {empty_spots} vacant spots (live)
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            ui.prediction_badge(label, conf)
            st.write("")

            b1, b2 = st.columns([3, 1])
            with b1:
                if st.button("View Details →", key=f"view_{lot['id']}", use_container_width=True):
                    st.session_state.selected_lot_id = lot["id"]
                    st.rerun()
            with b2:
                fav_icon = "💔" if is_fav else "❤️"
                if st.button(fav_icon, key=f"fav_{lot['id']}", use_container_width=True):
                    added = db.toggle_favorite(st.session_state.user_email, lot["id"])
                    st.toast("Added to favorites!" if added else "Removed from favorites.")
                    st.rerun()

    if not filtered:
        st.info("No parking lots match your filters. Try widening your search.")


# ════════════════════════════════════════════════════════════════
#  DETAIL + BOOKING VIEW
# ════════════════════════════════════════════════════════════════
def render_detail(lot):
    ui.top_header(f"📍 {lot['name']}", lot["address"])

    if st.button("← Back to results"):
        st.session_state.selected_lot_id = None
        st.rerun()

    left, right = st.columns([1.3, 1], gap="large")

    with left:
        if lot.get("image"):
            st.image(lot["image"], use_container_width=True)

        st.html("#### 🚙 Prediction by Vehicle Type")
        st.caption("Your dataset trains on vehicle type as a feature — pick one to see how the "
                   "model's prediction changes for this lot, right now.")
        chosen_vehicle = st.selectbox("Vehicle Type", VEHICLE_TYPES,
                                       index=VEHICLE_TYPES.index(lot.get("vehicle_type", "Car"))
                                       if lot.get("vehicle_type", "Car") in VEHICLE_TYPES else 0,
                                       key="detail_vehicle_type")
        pred_lot = dict(lot)
        pred_lot["vehicle_type"] = chosen_vehicle
        label, conf, empty_spots, occupied_spots, meta = predict_for_lot(pred_lot)

        m1, m2, m3 = st.columns(3)
        with m1: ui.stat_card("🏗️", "Capacity", lot["capacity"])
        with m2: ui.stat_card("💰", "Price / hr", f"₹{lot['price_per_hour']}")
        with m3: ui.stat_card("⭐", "Rating", f"{lot['rating']:.1f}")

        # Render the GPS satellite widget detailing tracking and real-time vacant estimation
        ui.live_occupancy_widget(meta, empty_spots, occupied_spots, lot["capacity"])

        with st.container(border=True):
            st.markdown("**🤖 AI Occupancy Prediction (live, right now)**")
            ui.prediction_badge(label, conf)
            st.caption("Prediction generated by the trained XGBoost model using time-of-day, zone, "
                       "and vehicle-type features — same pipeline as the original notebook.")

        st.markdown("#### 🏷️ Amenities")
        st.markdown(" ".join(ui.badge(a, "indigo") for a in lot.get("amenities", [])), unsafe_allow_html=True)

        st.markdown("#### 🗺️ Location")
        ui.google_map_view([lot], center_lat=lot["lat"], center_lng=lot["lng"], height=300)

        is_fav = lot["id"] in db.get_favorites(st.session_state.user_email)
        if st.button("💔 Remove from Favorites" if is_fav else "❤️ Add to Favorites"):
            db.toggle_favorite(st.session_state.user_email, lot["id"])
            st.rerun()

    with right:
        with st.container(border=True):
            st.markdown("### 🎫 Reserve a Spot")

            if st.session_state.booking_step == "form":
                with st.form("reserve_form", border=False):
                    date = st.date_input("Date", min_value=datetime.now().date())
                    time_val = st.time_input("Arrival Time", value=(datetime.now() + timedelta(minutes=30)).time())
                    duration = st.slider("Duration (hours)", 1, 12, 2)
                    vehicle_number = st.text_input(
                        "Vehicle Number", value=db.get_user(st.session_state.user_email).get("vehicle", ""))
                    vehicle_type = st.selectbox("Vehicle Type", VEHICLE_TYPES,
                                                 index=VEHICLE_TYPES.index(chosen_vehicle))
                    amount = round(duration * lot["price_per_hour"], 2)
                    st.markdown(f"**Estimated Total: ₹{amount:.2f}**  ({duration}h × ₹{lot['price_per_hour']}/hr)")
                    go = st.form_submit_button("Continue to Payment →", type="primary", use_container_width=True)

                if go:
                    if not vehicle_number.strip():
                        st.warning("Please enter your vehicle number.")
                    else:
                        st.session_state.pending_booking = {
                            "lot_id": lot["id"], "lot_name": lot["name"],
                            "slot_time": f"{date} {time_val.strftime('%H:%M')}",
                            "duration_hrs": duration, "vehicle_number": vehicle_number.strip(),
                            "vehicle_type": vehicle_type, "amount": amount,
                        }
                        st.session_state.razorpay_order = create_order(
                            amount, notes={"lot": lot["name"], "user": st.session_state.user_email})
                        st.session_state.booking_step = "pay"
                        st.rerun()

            elif st.session_state.booking_step == "pay":
                pb = st.session_state.pending_booking
                order = st.session_state.razorpay_order
                st.markdown("##### 💳 Checkout")
                st.caption(f"Razorpay Order ID: `{order['id']}` (placeholder — no real charge is made)")
                st.markdown(f"**{pb['lot_name']}** · {pb['slot_time']} · {pb['duration_hrs']}h")
                st.markdown(f"### ₹{pb['amount']:.2f}")

                method = st.radio("Payment Method", ["UPI", "Card", "Netbanking", "Wallet"], horizontal=True)

                pc1, pc2 = st.columns(2)
                with pc1:
                    if st.button("✅ Pay Now", type="primary", use_container_width=True):
                        payment = capture_payment(order, method=method.lower())
                        booking = db.create_booking(
                            st.session_state.user_email, lot["id"],
                            {**pb, "razorpay_order_id": order["id"], "razorpay_payment_id": payment["id"],
                             "payment_method": method, "status": "Confirmed"})
                        st.session_state.last_booking = booking
                        db.push_notification(
                            st.session_state.user_email,
                            f"Booking confirmed at {lot['name']} for {pb['slot_time']} — ₹{pb['amount']:.2f} paid.",
                            "success")
                        st.session_state.booking_step = "done"
                        st.rerun()
                with pc2:
                    if st.button("← Back", use_container_width=True):
                        st.session_state.booking_step = "form"
                        st.rerun()

            elif st.session_state.booking_step == "done":
                booking = st.session_state.last_booking
                st.success("🎉 Booking Confirmed!")
                st.balloons()
                st.markdown(f"**Booking ID:** `{booking['id']}`")
                st.markdown(f"**Lot:** {booking['lot_name']}  \n**Slot:** {booking['slot_time']}  \n"
                            f"**Vehicle:** {booking.get('vehicle_type','—')} · {booking.get('vehicle_number','—')}  \n"
                            f"**Duration:** {booking['duration_hrs']}h  \n**Amount Paid:** ₹{booking['amount']:.2f}")

                qr_bytes = generate_booking_qr(booking)
                st.image(qr_bytes, caption="Scan at entry gate", width=220)
                st.download_button("⬇️ Download QR Code", data=qr_bytes,
                                    file_name=f"{booking['id']}_qr.png", mime="image/png",
                                    use_container_width=True)

                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("🎫 View My Bookings", use_container_width=True):
                        st.session_state.selected_lot_id = None
                        st.switch_page("pages/3_👤_Account.py")
                with bc2:
                    if st.button("🅿️ Book Another Spot", use_container_width=True):
                        st.session_state.selected_lot_id = None
                        st.rerun()


# ── Router ──────────────────────────────────────────────────────
lot = db.get_lot(lot_id) if lot_id else None
if lot:
    render_detail(lot)
else:
    render_browse()