import random
import math
from datetime import datetime

# Simulated satellite telemetry database
SATELLITE_CONSTELLATIONS = [
    {"name": "NAVSTAR GPS IIF-1", "prn": "PRN 01", "signal": "L1/L2/L5", "elevation": 42.5, "azimuth": 118.2},
    {"name": "NAVSTAR GPS IIF-8", "prn": "PRN 03", "signal": "L1/L2", "elevation": 58.1, "azimuth": 242.0},
    {"name": "NAVSTAR GPS III-3", "prn": "PRN 12", "signal": "L1C/L5", "elevation": 67.4, "azimuth": 89.5},
    {"name": "GLONASS Cosmos-2545", "prn": "PRN 74", "signal": "G1/G2", "elevation": 28.3, "azimuth": 312.4},
    {"name": "GALILEO GSAT-0220", "prn": "PRN E14", "signal": "E1/E5a/E6", "elevation": 71.2, "azimuth": 15.6},
    {"name": "BEIDOU-3 M19", "prn": "PRN C21", "signal": "B1C/B2a", "elevation": 53.8, "azimuth": 167.3},
    {"name": "NAVSTAR GPS IIR-20", "prn": "PRN 17", "signal": "L1/L2", "elevation": 15.9, "azimuth": 204.8},
    {"name": "GALILEO GSAT-0223", "prn": "PRN E31", "signal": "E1/E5b", "elevation": 82.1, "azimuth": 88.0}
]

def get_satellite_telemetry(lat, lng):
    """
    Generates real-time GPS satellite telemetry data based on current coordinates & timestamp.
    Simulates orbit calculations and returns detailed tracking metrics.
    """
    now = datetime.now()
    seed = int(math.floor(lat * 100) + math.floor(lng * 100) + now.minute)
    rng = random.Random(seed)
    
    # Active satellites in view (typically 6-11 depending on terrain/orbit)
    num_sats = rng.randint(6, len(SATELLITE_CONSTELLATIONS))
    active_sats = rng.sample(SATELLITE_CONSTELLATIONS, num_sats)
    
    # Compute dilution of precision (DOP) metrics
    hdop = round(rng.uniform(0.7, 1.3), 2)  # Horizontal DOP
    vdop = round(rng.uniform(0.9, 1.6), 2)  # Vertical DOP
    pdop = round(math.sqrt(hdop**2 + vdop**2), 2)  # Position DOP
    
    # Estimate vehicle density around target coordinates based on simulated passive satellite RF noise
    # (High density = higher occupancy probability in the area)
    traffic_density = rng.randint(20, 180) # vehicles in 150m radius
    
    return {
        "satellites_tracked": num_sats,
        "satellites": active_sats,
        "dilution_of_precision": {
            "hdop": hdop,
            "vdop": vdop,
            "pdop": pdop
        },
        "traffic_density_gps": traffic_density,
        "signal_lock": True,
        "reference_station": "AP-VJW-RTK1"
    }

def estimate_empty_lots_gps(lot, telemetry):
    """
    Combines the GPS satellite density metrics and the physical lot attributes
    to calculate a live real-time empty lots estimate.

    Vehicle type matters here: each vehicle class competes for a different
    pool of spots (motorcycle bays, EV charging bays, oversized truck bays,
    standard car spots), so switching vehicle type shifts the occupancy
    estimate — not just the model's Vacant/Occupied label.
    """
    capacity = lot.get("capacity", 100)
    density = telemetry["traffic_density_gps"]

    # Base occupancy percent derived from density: higher GPS density -> more filled spaces
    # Combined with seasonal availability bias of the parking lot
    bias = lot.get("availability_bias", 0.5)

    # Calculate simulated occupied parking spots
    occupancy_rate = (density / 200.0) * (2.0 - bias)

    # Vehicle-type demand factor: Motorcycles fit into a larger, more plentiful
    # bay pool (lower effective occupancy). EVs and Trucks compete for a
    # scarcer, dedicated pool of spots (EV charging bays / oversized bays),
    # so they read as more heavily occupied for the same lot right now.
    vehicle_factor = {
        "Car": 1.00,
        "Motorcycle": 0.72,
        "Electric Vehicle": 1.22,
        "Truck": 1.35,
    }.get(lot.get("vehicle_type", "Car"), 1.00)
    occupancy_rate *= vehicle_factor

    occupancy_rate = max(0.1, min(0.95, occupancy_rate))

    # Add minor noise based on actual minute to make it fluctuate realistically in real time
    minute_factor = math.sin(datetime.now().minute / 10.0) * 0.05
    occupancy_rate = max(0.05, min(0.98, occupancy_rate + minute_factor))

    occupied = int(round(capacity * occupancy_rate))
    empty = max(0, capacity - occupied)

    return empty, occupied