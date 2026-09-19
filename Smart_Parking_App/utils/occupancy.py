"""
Live Occupancy Estimation
==========================
This replaces an earlier version of the app that simulated GPS satellite
telemetry (fake satellite lists, random PDOP/HDOP values, random "RF traffic
density") and presented it as if it were live hardware data. That was
misleading and has been removed.

Occupancy is now derived from data the app actually has:
  1. A static per-lot utilization baseline (`availability_bias` in the lot
     record) — this is seed/demo metadata, not a live sensor reading.
  2. Real, currently-active CONFIRMED bookings for that lot (from
     utils.data_store), which genuinely move the needle when a user books
     a spot in this demo.
  3. A vehicle-type factor: EVs and trucks compete for a scarcer, dedicated
     pool of spots (EV charging bays / oversized bays); motorcycles fit a
     larger, more plentiful bay pool. This is a stated lot-design
     assumption, not a fabricated sensor reading.

Future scope: replace the static baseline with real IoT occupancy sensors
(ultrasonic/magnetometer per spot) and/or RTK-GPS reference stations for
genuine live vehicle detection — see README "Future Scope".
"""

import math
from datetime import datetime, timedelta

from utils import data_store as db

VEHICLE_SPOT_FACTOR = {
    "Car": 1.00,
    "Motorcycle": 0.72,
    "Electric Vehicle": 1.22,
    "Truck": 1.35,
}


def _active_bookings_now(lot_id, vehicle_type, when):
    """Count CONFIRMED bookings for this lot whose time window covers `when`."""
    total, matching_vehicle = 0, 0
    for b in db.list_bookings(lot_id=lot_id):
        if b.get("status") != "Confirmed":
            continue
        try:
            start = datetime.strptime(b["slot_time"], "%Y-%m-%d %H:%M")
        except (KeyError, ValueError):
            continue
        end = start + timedelta(hours=float(b.get("duration_hrs", 1)))
        if start <= when <= end:
            total += 1
            if b.get("vehicle_type") == vehicle_type:
                matching_vehicle += 1
    return total, matching_vehicle


def compute_live_occupancy(lot, when=None):
    """Return (empty_spots, occupied_spots, meta).

    meta is an honestly-labeled dict describing where the numbers came
    from, for display in the UI (no fabricated sensor jargon).
    """
    when = when or datetime.now()
    capacity = lot.get("capacity", 100)
    vehicle_type = lot.get("vehicle_type", "Car")

    baseline = lot.get("availability_bias", 0.5)
    vehicle_factor = VEHICLE_SPOT_FACTOR.get(vehicle_type, 1.00)

    active_bookings, active_for_vehicle = _active_bookings_now(lot["id"], vehicle_type, when)

    baseline_rate = max(0.05, min(0.95, baseline * vehicle_factor))
    baseline_occupied = int(round(capacity * baseline_rate))

    occupied = min(capacity, baseline_occupied + active_bookings)
    empty = max(0, capacity - occupied)

    meta = {
        "active_bookings_now": active_bookings,
        "active_bookings_this_vehicle_type": active_for_vehicle,
        "baseline_utilization_pct": round(baseline_rate * 100, 1),
        "vehicle_type": vehicle_type,
        "last_updated": when.strftime("%H:%M:%S"),
        "source": "Live bookings + lot utilization baseline",
    }
    return empty, occupied, meta
