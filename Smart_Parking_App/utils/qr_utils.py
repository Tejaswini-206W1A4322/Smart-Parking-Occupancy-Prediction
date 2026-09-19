import io
import json
import qrcode
from qrcode.constants import ERROR_CORRECT_M


def generate_booking_qr(booking: dict) -> bytes:
    """Encode the key booking fields into a QR code and return PNG bytes."""
    payload = {
        "booking_id": booking.get("id"),
        "lot_id": booking.get("lot_id"),
        "lot_name": booking.get("lot_name"),
        "slot_time": booking.get("slot_time"),
        "duration_hrs": booking.get("duration_hrs"),
        "vehicle": booking.get("vehicle_number"),
        "amount": booking.get("amount"),
        "status": booking.get("status"),
    }
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(json.dumps(payload))
    qr.make(fit=True)
    img = qr.make_image(fill_color="#111827", back_color="#FFFFFF")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
