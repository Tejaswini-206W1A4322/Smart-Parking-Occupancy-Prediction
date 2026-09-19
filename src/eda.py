# ================================================================
#  eda.py
#  Handles: all exploratory data analysis and visualisation
#  Usage  : from eda import run_eda
# ================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams["figure.dpi"] = 120


def plot_occupancy_overview(df: pd.DataFrame, output_dir: str):
    """Plot 1: Class balance pie + occupancy rate per parking spot."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Occupancy Overview", fontsize=14, fontweight="bold")

    occ_counts = df["Occupancy_Status"].value_counts()
    colors = ["#EF5350", "#42A5F5"]
    axes[0].pie(
        occ_counts, labels=occ_counts.index,
        autopct="%1.1f%%", colors=colors, startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    axes[0].set_title("Class Balance")

    spot_occ = df.groupby("Parking_Spot_ID")["occupied"].mean() * 100
    axes[1].bar(spot_occ.index, spot_occ.values,
                color="#42A5F5", alpha=0.8)
    axes[1].axhline(spot_occ.mean(), color="red", linestyle="--",
                    label=f"Average: {spot_occ.mean():.1f}%")
    axes[1].set_title("Occupancy Rate per Parking Spot")
    axes[1].set_xlabel("Parking Spot ID")
    axes[1].set_ylabel("Occupancy Rate (%)")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(f"{output_dir}01_occupancy_overview.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot 1 saved: 01_occupancy_overview.png")


def plot_temporal_patterns(df: pd.DataFrame, output_dir: str):
    """Plot 2: Heatmap, hourly average, daily, and monthly patterns."""
    df = df.copy()
    df["hour"]        = df["Timestamp"].dt.hour
    df["day_of_week"] = df["Timestamp"].dt.dayofweek
    df["day_name"]    = df["Timestamp"].dt.day_name()
    df["month"]       = df["Timestamp"].dt.month

    day_order = ["Monday","Tuesday","Wednesday",
                 "Thursday","Friday","Saturday","Sunday"]

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Temporal Occupancy Patterns", fontsize=14, fontweight="bold")

    # Heatmap
    pivot = df.groupby(["day_name","hour"])["occupied"].mean().unstack()
    pivot = pivot.reindex(day_order)
    sns.heatmap(pivot, ax=axes[0,0], cmap="YlOrRd",
                linewidths=0.3, cbar_kws={"label":"Occupancy Rate"})
    axes[0,0].set_title("Heatmap — Hour × Day of Week")
    axes[0,0].set_xlabel("Hour of Day")

    # Hourly
    hourly = df.groupby("hour")["occupied"].mean() * 100
    axes[0,1].fill_between(hourly.index, hourly.values, alpha=0.4, color="#2196F3")
    axes[0,1].plot(hourly.index, hourly.values, "o-", color="#1565C0", linewidth=2)
    axes[0,1].set_title("Average Occupancy by Hour")
    axes[0,1].set_xlabel("Hour of Day")
    axes[0,1].set_ylabel("Occupancy Rate (%)")
    axes[0,1].set_xticks(range(0, 24, 2))

    # Daily
    daily = df.groupby("day_name")["occupied"].mean().reindex(day_order) * 100
    bar_colors = ["#FF7043" if d in ["Saturday","Sunday"]
                  else "#42A5F5" for d in day_order]
    axes[1,0].bar(day_order, daily.values,
                  color=bar_colors, edgecolor="white")
    axes[1,0].set_title("Occupancy by Day  (orange = weekend)")
    axes[1,0].set_ylabel("Occupancy Rate (%)")
    axes[1,0].tick_params(axis="x", rotation=30)

    # Monthly
    monthly = df.groupby("month")["occupied"].mean() * 100
    axes[1,1].plot(monthly.index, monthly.values,
                   "s-", color="#66BB6A", linewidth=2, markersize=8)
    axes[1,1].fill_between(monthly.index, monthly.values,
                            alpha=0.2, color="#66BB6A")
    axes[1,1].set_title("Monthly Occupancy Trend")
    axes[1,1].set_xlabel("Month")
    axes[1,1].set_ylabel("Occupancy Rate (%)")

    plt.tight_layout()
    plt.savefig(f"{output_dir}02_temporal_patterns.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot 2 saved: 02_temporal_patterns.png")


def plot_sensor_analysis(df: pd.DataFrame, output_dir: str):
    """Plot 3: Sensor distributions and box plots by occupancy class."""
    sensor_cols = [
        "Sensor_Reading_Proximity",
        "Sensor_Reading_Pressure",
        "Sensor_Reading_Ultrasonic",
    ]
    colors_map = {"Occupied": "#EF5350", "Vacant": "#42A5F5"}

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Sensor Analysis — Occupied vs Vacant",
                 fontsize=14, fontweight="bold")

    for i, sensor in enumerate(sensor_cols):
        # Distribution
        for status in ["Occupied", "Vacant"]:
            subset = df[df["Occupancy_Status"] == status][sensor]
            axes[0, i].hist(subset, bins=30, alpha=0.6,
                            label=status, color=colors_map[status],
                            density=True)
        axes[0, i].set_title(f"{sensor.replace('Sensor_Reading_','')}\nDistribution")
        axes[0, i].set_xlabel("Sensor Value")
        axes[0, i].set_ylabel("Density")
        axes[0, i].legend()

        # Box plot
        sns.boxplot(data=df, x="Occupancy_Status", y=sensor,
                    ax=axes[1, i], palette=colors_map,
                    order=["Vacant", "Occupied"])
        axes[1, i].set_title(f"{sensor.replace('Sensor_Reading_','')}\nBox Plot")
        axes[1, i].set_xlabel("")

        # T-test
        occ = df[df["Occupancy_Status"] == "Occupied"][sensor]
        vac = df[df["Occupancy_Status"] == "Vacant"][sensor]
        _, p_val = stats.ttest_ind(occ, vac)
        axes[1, i].text(0.98, 0.95, f"p = {p_val:.3f}",
                        transform=axes[1, i].transAxes,
                        ha="right", va="top", fontsize=9,
                        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    plt.savefig(f"{output_dir}03_sensor_analysis.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot 3 saved: 03_sensor_analysis.png")


def plot_external_factors(df: pd.DataFrame, output_dir: str):
    """Plot 4: Traffic, vehicle type, zone, and temperature vs occupancy."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("External Factors vs Occupancy",
                 fontsize=14, fontweight="bold")

    # Traffic
    traffic_occ = (df.groupby("Nearby_Traffic_Level")["occupied"]
                   .mean().reindex(["Low","Medium","High"]) * 100)
    axes[0,0].bar(traffic_occ.index, traffic_occ.values,
                  color=["#66BB6A","#FFA726","#EF5350"],
                  edgecolor="white", width=0.5)
    axes[0,0].set_title("Traffic Level vs Occupancy")
    axes[0,0].set_ylabel("Avg Occupancy (%)")

    # Vehicle type
    vehicle_occ = (df.groupby("Vehicle_Type")["occupied"]
                   .mean() * 100)
    axes[0,1].bar(vehicle_occ.index, vehicle_occ.values,
                  color="#7E57C2", edgecolor="white", width=0.5)
    axes[0,1].set_title("Vehicle Type vs Occupancy")
    axes[0,1].set_ylabel("Avg Occupancy (%)")

    # Zone
    zone_occ = (df.groupby("Parking_Lot_Section")["occupied"]
                .mean() * 100)
    axes[1,0].bar(zone_occ.index, zone_occ.values,
                  color="#26C6DA", edgecolor="white", width=0.5)
    axes[1,0].set_title("Parking Zone vs Occupancy")
    axes[1,0].set_ylabel("Avg Occupancy (%)")

    # Temperature
    temp_bins = pd.cut(df["Weather_Temperature"], bins=10)
    temp_occ  = (df.groupby(temp_bins, observed=True)["occupied"]
                 .mean() * 100)
    axes[1,1].plot(range(len(temp_occ)), temp_occ.values,
                   "o-", color="#EF5350", linewidth=2)
    axes[1,1].set_title("Temperature vs Occupancy")
    axes[1,1].set_xlabel("Temperature (low → high, binned)")
    axes[1,1].set_ylabel("Avg Occupancy (%)")
    axes[1,1].set_xticks([])

    plt.tight_layout()
    plt.savefig(f"{output_dir}04_external_factors.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot 4 saved: 04_external_factors.png")


def plot_correlation_matrix(df: pd.DataFrame, output_dir: str):
    """Plot 5: Correlation heatmap of numeric features vs target."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    exclude      = ["Parking_Spot_ID", "Occupancy_Rate", "occupied"]
    corr_cols    = [c for c in numeric_cols if c not in exclude]

    corr_matrix = df[corr_cols + ["occupied"]].corr()

    plt.figure(figsize=(16, 12))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f",
                cmap="RdBu_r", center=0, square=True,
                linewidths=0.5, annot_kws={"size": 7},
                cbar_kws={"shrink": 0.7})
    plt.title("Feature Correlation Matrix",
              fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(f"{output_dir}05_correlation_matrix.png",
                dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot 5 saved: 05_correlation_matrix.png")


def run_eda(df: pd.DataFrame, output_dir: str):
    """Run all 5 EDA plots in sequence."""
    print("\n" + "=" * 50)
    print("  EXPLORATORY DATA ANALYSIS")
    print("=" * 50)

    plot_occupancy_overview(df, output_dir)
    plot_temporal_patterns(df, output_dir)
    plot_sensor_analysis(df, output_dir)
    plot_external_factors(df, output_dir)
    plot_correlation_matrix(df, output_dir)

    print("\nAll 5 EDA plots saved to outputs/")
