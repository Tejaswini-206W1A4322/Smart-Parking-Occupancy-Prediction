import streamlit as st
from utils import data_store as db


def init_session():
    defaults = {
        "logged_in": False,
        "user_email": None,
        "user_name": "",
        "user_role": "user",
        "selected_lot_id": None,
        "last_booking": None,
        "booking_step": "browse",
        "booking_step_lot_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def login(email, name, role):
    st.session_state.logged_in = True
    st.session_state.user_email = email
    st.session_state.user_name = name
    st.session_state.user_role = role


def logout():
    for k in ["logged_in", "user_email", "user_name", "user_role"]:
        st.session_state[k] = False if k == "logged_in" else None
    st.session_state.user_role = "user"


def require_login():
    """Call at the top of every protected page. Redirects to the login/home page."""
    init_session()
    if not st.session_state.logged_in:
        st.warning("🔒 Please sign in to access this page.")
        if st.button("Go to Sign In"):
            st.switch_page("app.py")
        st.stop()


def require_role(*roles):
    require_login()
    if st.session_state.user_role not in roles:
        st.error("⛔ You don't have permission to view this page.")
        st.caption(f"This page is restricted to: {', '.join(roles)}")
        st.stop()


def current_user():
    u = db.get_user(st.session_state.user_email) if st.session_state.get("user_email") else None
    return u
