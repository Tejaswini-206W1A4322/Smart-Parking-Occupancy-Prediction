"""
Payment Integration — Razorpay (PLACEHOLDER)
=============================================
These functions mirror the shape of the real Razorpay Python SDK
(`razorpay.Client(auth=(key_id, key_secret))`) so swapping in the live SDK
later is a drop-in change. No real network calls are made here — orders and
payments are simulated locally, which is exactly what this project layer
needs since only the application layer (not billing infrastructure) is in
scope.

To go live:
    pip install razorpay
    client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
    order = client.order.create({...})
    client.utility.verify_payment_signature({...})
"""

import uuid
import time
import hmac
import hashlib
import streamlit as st


def get_razorpay_keys():
    try:
        key_id = st.secrets["RAZORPAY_KEY_ID"]
    except Exception:
        key_id = "rzp_test_placeholder"
    try:
        key_secret = st.secrets["RAZORPAY_KEY_SECRET"]
    except Exception:
        key_secret = "placeholder_secret"
    return key_id, key_secret


def create_order(amount_rupees: float, receipt: str = None, notes: dict = None):
    """Placeholder for client.order.create(). Returns a mock Razorpay order dict."""
    key_id, _ = get_razorpay_keys()
    order = {
        "id": f"order_{uuid.uuid4().hex[:14]}",
        "entity": "order",
        "amount": int(round(amount_rupees * 100)),  # paise, like the real API
        "amount_paid": 0,
        "amount_due": int(round(amount_rupees * 100)),
        "currency": "INR",
        "receipt": receipt or f"receipt_{uuid.uuid4().hex[:8]}",
        "status": "created",
        "notes": notes or {},
        "created_at": int(time.time()),
        "key_id": key_id,
    }
    return order


def capture_payment(order: dict, method: str = "upi"):
    """Placeholder for the checkout hand-off + client.payment.capture().

    In production this would run client-side via Razorpay Checkout.js and be
    confirmed server-side. Here we simulate an instant successful capture so
    the booking flow can be demoed end-to-end.
    """
    payment_id = f"pay_{uuid.uuid4().hex[:14]}"
    signature = hmac.new(
        get_razorpay_keys()[1].encode(), payment_id.encode(), hashlib.sha256
    ).hexdigest()
    payment = {
        "id": payment_id,
        "entity": "payment",
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "status": "captured",
        "method": method,
        "captured": True,
        "signature": signature,
        "created_at": int(time.time()),
    }
    return payment


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Placeholder for client.utility.verify_payment_signature(). Always
    recomputes locally against our own mock HMAC rather than calling out."""
    expected = hmac.new(
        get_razorpay_keys()[1].encode(), payment_id.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def refund_payment(payment_id: str, amount_rupees: float = None):
    """Placeholder for client.payment.refund()."""
    return {
        "id": f"rfnd_{uuid.uuid4().hex[:14]}",
        "entity": "refund",
        "payment_id": payment_id,
        "amount": int(round(amount_rupees * 100)) if amount_rupees else None,
        "status": "processed",
        "created_at": int(time.time()),
    }
