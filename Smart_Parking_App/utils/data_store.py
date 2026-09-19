"""
Lightweight JSON-backed "database" for the demo/commercial application layer.

This keeps users, parking lots, bookings, favorites and notifications in a
single JSON file on disk (data/db.json) so state survives across reruns and
is shared between the User / Admin / Owner dashboards — without requiring a
real database server for this project layer.
"""

import json
import os
import uuid
import hashlib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "db.json")
SEED_LOTS_PATH = os.path.join(BASE_DIR, "data", "parking_locations.json")

_DEFAULT_DB = {
    "users": {},
    "lots": [],
    "bookings": [],
    "favorites": {},
    "notifications": {},
}


def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _load_seed_lots():
    if os.path.exists(SEED_LOTS_PATH):
        with open(SEED_LOTS_PATH, "r") as f:
            return json.load(f)
    return []


def _ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        db = json.loads(json.dumps(_DEFAULT_DB))
        db["lots"] = _load_seed_lots()
        demo_users = [
            ("demo@smartparking.ai", "Demo User", "Demo1234!", "user"),
            ("admin@smartparking.ai", "Platform Admin", "Admin1234!", "admin"),
            ("owner@smartparking.ai", "Lot Owner", "Owner1234!", "owner"),
        ]
        for email, name, pw, role in demo_users:
            db["users"][email] = {
                "name": name, "password": _hash_pw(pw), "role": role,
                "phone": "9000000000", "vehicle": "AP 16 AB 1234",
                "created_at": datetime.now().isoformat(),
            }
        db["favorites"] = {u: [] for u in db["users"]}
        db["notifications"] = {u: [] for u in db["users"]}
        _save(db)
        return db
    with open(DB_PATH, "r") as f:
        return json.load(f)


def verify_phone_login(phone, password):
    db = load_db()
    sanitized_phone = "".join([c for c in phone if c.isdigit()])
    if not sanitized_phone:
        return False, "Invalid phone number."
    for email, u in db["users"].items():
        db_phone = "".join([c for c in u.get("phone", "") if c.isdigit()])
        if db_phone == sanitized_phone:
            if u["password"] == _hash_pw(password):
                return True, {"email": email, "name": u["name"], "role": u["role"]}
            else:
                return False, "Incorrect password."
    return False, "No account found with that phone number."



def _save(db):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2, default=str)


def load_db():
    return _ensure_db()


# ── Users / Auth ────────────────────────────────────────────────
def get_user(email):
    db = load_db()
    return db["users"].get(email)


def create_user(email, name, password, role="user", phone="", vehicle=""):
    db = load_db()
    if email in db["users"]:
        return False, "An account with this email already exists."
    db["users"][email] = {
        "name": name, "password": _hash_pw(password), "role": role,
        "phone": phone, "vehicle": vehicle,
        "created_at": datetime.now().isoformat(),
    }
    db["favorites"].setdefault(email, [])
    db["notifications"].setdefault(email, [])
    _save(db)
    return True, "Account created."


def verify_login(email, password):
    user = get_user(email)
    if not user:
        return False, "No account found with that email."
    if user["password"] != _hash_pw(password):
        return False, "Incorrect password."
    return True, user


def update_profile(email, **fields):
    db = load_db()
    if email not in db["users"]:
        return False
    db["users"][email].update(fields)
    _save(db)
    return True


# ── Parking Lots ────────────────────────────────────────────────
def list_lots(owner_email=None):
    db = load_db()
    lots = db["lots"]
    if owner_email:
        lots = [l for l in lots if l.get("owner_email") == owner_email]
    return lots


def get_lot(lot_id):
    db = load_db()
    for l in db["lots"]:
        if l["id"] == lot_id:
            return l
    return None


def add_lot(lot: dict):
    db = load_db()
    lot["id"] = lot.get("id") or f"lot_{uuid.uuid4().hex[:8]}"
    db["lots"].append(lot)
    _save(db)
    return lot["id"]


def update_lot(lot_id, **fields):
    db = load_db()
    for l in db["lots"]:
        if l["id"] == lot_id:
            l.update(fields)
            _save(db)
            return True
    return False


# ── Bookings ────────────────────────────────────────────────────
def create_booking(user_email, lot_id, booking: dict):
    db = load_db()
    booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
    record = {
        "id": booking_id,
        "user_email": user_email,
        "lot_id": lot_id,
        "created_at": datetime.now().isoformat(),
        "status": "Confirmed",
        **booking,
    }
    db["bookings"].append(record)
    _save(db)
    return record


def list_bookings(user_email=None, lot_id=None, owner_email=None):
    db = load_db()
    bookings = db["bookings"]
    if user_email:
        bookings = [b for b in bookings if b["user_email"] == user_email]
    if lot_id:
        bookings = [b for b in bookings if b["lot_id"] == lot_id]
    if owner_email:
        owned_ids = {l["id"] for l in db["lots"] if l.get("owner_email") == owner_email}
        bookings = [b for b in bookings if b["lot_id"] in owned_ids]
    return sorted(bookings, key=lambda b: b["created_at"], reverse=True)


def update_booking_status(booking_id, status):
    db = load_db()
    for b in db["bookings"]:
        if b["id"] == booking_id:
            b["status"] = status
            _save(db)
            return True
    return False


# ── Favorites ───────────────────────────────────────────────────
def get_favorites(user_email):
    db = load_db()
    return db["favorites"].get(user_email, [])


def toggle_favorite(user_email, lot_id):
    db = load_db()
    favs = db["favorites"].setdefault(user_email, [])
    if lot_id in favs:
        favs.remove(lot_id)
        added = False
    else:
        favs.append(lot_id)
        added = True
    _save(db)
    return added


# ── Notifications ───────────────────────────────────────────────
def push_notification(user_email, message, kind="info"):
    db = load_db()
    notes = db["notifications"].setdefault(user_email, [])
    notes.insert(0, {
        "message": message, "kind": kind, "read": False,
        "time": datetime.now().isoformat(),
    })
    db["notifications"][user_email] = notes[:50]
    _save(db)


def list_notifications(user_email):
    db = load_db()
    return db["notifications"].get(user_email, [])


def mark_all_read(user_email):
    db = load_db()
    for n in db["notifications"].get(user_email, []):
        n["read"] = True
    _save(db)


def unread_count(user_email):
    return sum(1 for n in list_notifications(user_email) if not n.get("read"))
