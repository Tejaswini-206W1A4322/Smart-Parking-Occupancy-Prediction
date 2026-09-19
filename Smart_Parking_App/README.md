# 🅿️ Smart Parking — AI-Driven Smart Occupancy Prediction

A commercial-style smart parking application built on top of your **existing,
unmodified** XGBoost occupancy model. Only the application layer is new —
the ML model, feature engineering, and prediction workflow are reused as-is.

## Pages (4 total)

```
app.py                              → Page 1: 3D interactive hero landing + Login/Register
pages/1_🏠_Dashboard.py              → Page 2: overview stats + live ML predictions
pages/2_🅿️_Find_and_Book.py          → Page 3: search/map/filter → details → reserve → pay → QR
pages/3_👤_Account.py                → Page 4: role-based —
                                          • Driver: Profile / Bookings / Favorites / Notifications
                                          • Admin:  platform analytics & moderation
                                          • Owner:  lot & booking management
```

## Project layout

```
smart_parking_app/
├── app.py
├── pages/1_🏠_Dashboard.py, 2_🅿️_Find_and_Book.py, 3_👤_Account.py
├── utils/
│   ├── prediction.py    # ⚠️ your model logic — UNCHANGED
│   ├── data_store.py    # JSON-backed mock database
│   ├── auth.py           # session/login/role guards
│   ├── payment.py        # Razorpay-style placeholder functions
│   ├── qr_utils.py        # QR code generation
│   ├── ui.py               # theme (indigo + orange, from the logo), cards, Google Maps
│   ├── hero.py              # Three.js 3D hero section for the landing page
│   └── sidebar.py            # sticky logo header (left panel), profile, logout
├── assets/logo.png
├── data/parking_locations.json
├── models/best_model.pkl, feature_cols.pkl   ← place your existing trained files here
├── .streamlit/config.toml, secrets.toml.example
└── requirements.txt
```

## Setup

```bash
cd smart_parking_app
pip install -r requirements.txt

# 1. Copy your existing trained model files (do not retrain):
#    models/best_model.pkl
#    models/feature_cols.pkl

# 2. (Optional) enable a live interactive Google Map:
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
#    edit .streamlit/secrets.toml -> GOOGLE_MAPS_API_KEY = "your_key"

streamlit run app.py
```

## Demo accounts (seeded automatically on first run)

| Role   | Gmail                     | Password   |
|--------|-----------------------------|------------|
| Driver | demo@smartparking.ai        | demo1234   |
| Admin  | admin@smartparking.ai       | admin1234  |
| Owner  | owner@smartparking.ai       | owner1234  |

## Design notes

- **Colors** come directly from your logo: deep indigo (`#0F0E3D` / `#2B3AA8`)
  for branding/headers, and orange (`#FD6231`) exclusively for call-to-action
  buttons (Sign In, Pay Now, Continue, etc.) so CTAs are always visually
  distinct. No dark-mode toggle — that was removed since it produced
  illegible black-on-black text; the app now uses one carefully-tuned,
  always-legible light theme (the hero's dark styling is isolated to its own
  iframe and doesn't affect any real widgets).
- **3D hero** (`utils/hero.py`) uses Three.js — a glowing wireframe icosahedron
  that tilts toward the mouse and glows brighter on hover — plus a GSAP
  fade/stagger-in for the feature cards beneath it.
- **Prediction display** shows only the model's actual output — a label and
  a confidence percentage — with no derived/fabricated numbers next to it,
  so nothing can visually contradict the model.
- **Vehicle type** (a real feature in your dataset) is now user-facing: a
  filter on the Find & Book page, and a live selector on the lot detail page
  that recomputes the prediction for the chosen vehicle type in real time.
- **Booking-confirmation bug fix**: the reservation flow's step (form → pay
  → confirmed) is now tracked per parking lot. Opening a different lot (or
  returning to a previously-viewed one) no longer inherits a stale
  "Confirmed" screen from an earlier, unrelated booking — you'll always see
  the correct step for the lot you're currently viewing.
- **No stray empty boxes**: anywhere a form, tabs, or buttons need a bordered
  card, the app uses Streamlit's native `st.container(border=True)` instead
  of a raw HTML `<div>` wrapper. Raw HTML divs are only ever used for
  content that has no real widgets inside it (badges, stat tiles, lot
  cards) — mixing the two was what caused an empty floating box on the
  sign-in section previously.

## What's mocked vs. real

- **Real:** your trained model + its exact preprocessing/feature pipeline.
- **Mocked (application-layer scope):** parking-lot inventory
  (`data/parking_locations.json`), the JSON file-backed "database"
  (`data/db.json`, created on first run), and Razorpay payment calls
  (`utils/payment.py` mirrors the real SDK's method signatures so swapping
  in `pip install razorpay` later is a drop-in change).
