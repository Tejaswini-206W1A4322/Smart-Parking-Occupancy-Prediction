# ================================================================
#  feature_engineering.py
#  Handles: temporal, cyclical, lag, sensor, categorical features
#  Usage  : from feature_engineering import build_features
# ================================================================

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract time-based features from Timestamp.
    hour, day_of_week, month, is_weekend, peak hour flags.
    """
    df["hour"]        = df["Timestamp"].dt.hour
    df["day_of_week"] = df["Timestamp"].dt.dayofweek
    df["month"]       = df["Timestamp"].dt.month
    df["is_weekend"]  = (df["day_of_week"] >= 5).astype(int)

    df["is_morning_peak"] = df["hour"].between(7,  9).astype(int)
    df["is_lunch_hour"]   = df["hour"].between(12, 14).astype(int)
    df["is_evening_peak"] = df["hour"].between(17, 19).astype(int)
    df["is_night"]        = df["hour"].between(22, 23).astype(int)

    print("Temporal features added!")
    print(f"   is_weekend      : {df['is_weekend'].sum()} records")
    print(f"   is_morning_peak : {df['is_morning_peak'].sum()} records")
    print(f"   is_evening_peak : {df['is_evening_peak'].sum()} records")
    return df


def add_cyclical_encoding(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encode hour, day, and month as sin/cos pairs.
    Preserves circular nature — hour 23 and hour 0 are neighbours.
    """
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"]        / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"]        / 24)
    df["day_sin"]  = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["day_cos"]  = np.cos(2 * np.pi * df["day_of_week"] / 7)

    print("Cyclical encoding added!")
    print("   hour_sin/cos → hour on a circle")
    print("   day_sin/cos  → day on a circle")
    return df


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add historical occupancy features per parking spot.
    These are the most predictive features — parking has memory.

    IMPORTANT: df must be sorted by Parking_Spot_ID → Timestamp
               before calling this function.
    """
    df = df.sort_values(
        ["Parking_Spot_ID", "Timestamp"]
    ).reset_index(drop=True)

    g = df.groupby("Parking_Spot_ID")["occupied"]

    # Lag features
    df["prev_occupancy"] = g.shift(1).fillna(0)

    # Rolling mean — smoothed recent history
    df["rolling_mean_3"] = g.transform(
        lambda x: x.shift(1).rolling(3, min_periods=1).mean()
    ).fillna(0)

    # Historical average for this spot at this hour
    df["spot_hour_avg"] = df.groupby(
        ["Parking_Spot_ID", "hour"]
    )["occupied"].transform("mean")

    print("Lag features added!")
    print("   prev_occupancy → what happened 1 step ago")
    print("   rolling_mean_3 → average of last 3 readings")
    print("   spot_hour_avg  → spot's usual behaviour at this hour")
    return df


def add_sensor_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create interaction features from the 3 sensor readings.
    Combined sensor signals are stronger than individual ones.
    """
    df["sensor_mean"] = df[[
        "Sensor_Reading_Proximity",
        "Sensor_Reading_Pressure",
        "Sensor_Reading_Ultrasonic",
    ]].mean(axis=1)

    print("Sensor interaction features added!")
    print("   sensor_mean → average of all 3 sensors")
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode categorical columns.
    drop_first=True avoids dummy variable trap.
    Boolean output converted to int for model compatibility.
    """
    cols_to_encode = [
        "Vehicle_Type",
        "User_Type",
        "Nearby_Traffic_Level",
        "Parking_Lot_Section",
        "Spot_Size",
        "Payment_Status",
    ]

    df = pd.get_dummies(df, columns=cols_to_encode, drop_first=True)

    bool_cols = df.select_dtypes(include="bool").columns
    df[bool_cols] = df[bool_cols].astype(int)

    print("Categorical encoding done!")
    print(f"   Shape after encoding: {df.shape}")
    return df


def build_feature_matrix(df: pd.DataFrame):
    """
    Remove metadata and leakage columns.
    Return X (features), y (target), feature_cols (list).

    Excluded columns explanation:
    - Timestamp      : already extracted into temporal features
    - Occupancy_Status: original text target
    - occupied       : numeric target — this is y
    - day_name       : text duplicate of day_of_week
    - Parking_Spot_ID: ID — not a predictive feature
    - Entry/Exit/Duration/Payment_Amount: leak future information
    - Occupancy_Rate : derived directly from target
    """
    exclude_cols = [
        "Timestamp", "Occupancy_Status", "occupied",
        "day_name", "Parking_Spot_ID",
        "Entry_Time", "Exit_Time",
        "Parking_Duration", "Payment_Amount",
        "Occupancy_Rate",
    ]

    feature_cols = [c for c in df.columns if c not in exclude_cols]

    X = df[feature_cols]
    y = df["occupied"]

    print("Feature matrix ready!")
    print(f"   X shape        : {X.shape}")
    print(f"   y shape        : {y.shape}")
    print(f"   Total features : {len(feature_cols)}")
    print(f"   Target balance : {y.mean()*100:.1f}% occupied")

    return X, y, feature_cols


def build_features(df_clean: pd.DataFrame):
    """
    Full feature engineering pipeline.
    Returns: df_feat, X, y, feature_cols
    """
    print("\n" + "=" * 50)
    print("  FEATURE ENGINEERING")
    print("=" * 50)

    df = df_clean.copy()
    df = add_temporal_features(df)
    df = add_cyclical_encoding(df)
    df = add_lag_features(df)
    df = add_sensor_features(df)
    df = encode_categoricals(df)

    X, y, feature_cols = build_feature_matrix(df)

    return df, X, y, feature_cols
