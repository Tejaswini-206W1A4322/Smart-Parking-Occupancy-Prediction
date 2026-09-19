# ================================================================
#  data_pipeline.py
#  Handles: loading, cleaning, and validating the dataset
#  Usage  : from data_pipeline import load_and_clean
# ================================================================

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")


def load_data(data_path: str) -> pd.DataFrame:
    """Load CSV from given path and print basic info."""
    df = pd.read_csv(data_path)
    print(f"Dataset loaded!")
    print(f"   Rows    : {df.shape[0]}")
    print(f"   Columns : {df.shape[1]}")
    return df


def parse_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """Convert Timestamp column to datetime format."""
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    print("Timestamp parsed successfully!")
    print(f"   Earliest : {df['Timestamp'].min()}")
    print(f"   Latest   : {df['Timestamp'].max()}")
    print(f"   Range    : {(df['Timestamp'].max() - df['Timestamp'].min()).days} days")
    return df


def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure correct data types for binary and float columns."""
    binary_cols = ["Electric_Vehicle", "Reserved_Status", "Parking_Violation"]
    for col in binary_cols:
        df[col] = df[col].astype(int)

    float_cols = [
        "Sensor_Reading_Proximity", "Sensor_Reading_Pressure",
        "Sensor_Reading_Ultrasonic", "Weather_Temperature",
        "Dynamic_Pricing_Factor", "Environmental_Noise_Level",
        "Proximity_To_Exit", "User_Parking_History",
        "Vehicle_Type_Weight", "Vehicle_Type_Height",
    ]
    for col in float_cols:
        df[col] = df[col].astype(float)

    print("Data types fixed!")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate rows if any exist."""
    n = df.duplicated().sum()
    if n > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        print(f"Removed {n} duplicate rows")
    else:
        print("No duplicate rows found!")
    print(f"   Shape after check : {df.shape}")
    return df


def validate_sensor_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clip sensor and weather readings to physically valid ranges.
    Out-of-range values are clipped rather than dropped.
    """
    sensor_checks = {
        "Sensor_Reading_Proximity"  : (0, 500),
        "Sensor_Reading_Pressure"   : (0, 10000),
        "Sensor_Reading_Ultrasonic" : (0, 500),
        "Weather_Temperature"       : (-20, 60),
        "Weather_Precipitation"     : (0, 500),
    }
    print("Sensor Range Validation")
    print("=" * 50)
    for col, (low, high) in sensor_checks.items():
        out_of_range = ((df[col] < low) | (df[col] > high)).sum()
        status = "OK" if out_of_range == 0 else f"{out_of_range} clipped"
        print(f"   {col:<35} {status}")
        df[col] = df[col].clip(low, high)
    print("All sensor values validated!")
    return df


def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """Encode Occupancy_Status as binary: Occupied=1, Vacant=0."""
    df["occupied"] = (df["Occupancy_Status"] == "Occupied").astype(int)
    print("Target encoded!")
    print(f"   Occupied : {df['occupied'].sum()}")
    print(f"   Vacant   : {(df['occupied'] == 0).sum()}")
    print(f"   Balance  : {df['occupied'].mean()*100:.1f}% occupied")
    return df


def load_and_clean(data_path: str) -> pd.DataFrame:
    """
    Full pipeline: load → parse → fix types → deduplicate
                   → validate sensors → encode target.
    Returns cleaned DataFrame ready for EDA.
    """
    print("\n" + "=" * 50)
    print("  DATA PIPELINE")
    print("=" * 50)

    df = load_data(data_path)
    df = parse_timestamp(df)
    df = fix_dtypes(df)
    df = remove_duplicates(df)
    df = validate_sensor_ranges(df)
    df = encode_target(df)

    print(f"\ndf_clean ready | shape: {df.shape}")
    return df
