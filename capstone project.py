import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


# ------------ Task 1: Data ingestion ------------

def load_data(data_dir="data"):
    all_frames = []
    for csv_file in Path(data_dir).glob("*.csv"):
        try:
            df = pd.read_csv(csv_file, on_bad_lines="skip")   # skip bad rows [web:27][web:31]
            # adjust column names here if your file uses different ones
            # expected columns: timestamp, kwh
            df["building"] = csv_file.stem
            all_frames.append(df)
        except FileNotFoundError:
            print(f"Missing file: {csv_file}")
        except Exception as e:
            print(f"Error in {csv_file}: {e}")

    if not all_frames:
        raise ValueError("No CSV files loaded from data folder")

    df_combined = pd.concat(all_frames, ignore_index=True)
    return df_combined


# ------------ Task 3: OOP classes ------------

class MeterReading:
    def _init_(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh


class Building:
    def _init_(self, name):
        self.name = name
        self.meter_readings = []

    def add_reading(self, reading: MeterReading):
        self.meter_readings.append(reading)

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.meter_readings)

    def generate_report(self):
        total = self.calculate_total_consumption()
        return f"Building {self.name} used {total} kWh"


class BuildingManager:
    def _init_(self):
        self.buildings = {}

    def get_building(self, name):
        if name not in self.buildings:
            self.buildings[name] = Building(name)
        return self.buildings[name]


# ------------ Task 2: aggregation functions ------------

def calculate_daily_totals(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    daily = (
        df.groupby(["building", pd.Grouper(key="timestamp", freq="D")])["kwh"]
        .sum()
        .reset_index()
    )
    return daily   # daily totals per building


def calculate_weekly_aggregates(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    weekly = (
        df.groupby(["building", pd.Grouper(key="timestamp", freq="W")])["kwh"]
        .sum()
        .reset_index()
    )
    return weekly  # weekly totals per building


def building_wise_summary(df):
    summary = (
        df.groupby("building")["kwh"]
        .agg(["mean", "min", "max", "sum"])
        .reset_index()
        .rename(columns={"sum": "total"})
    )
    return summary


# ------------ Task 4: plots ------------

def create_plots(daily_df, summary_df):
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # 1. Trend line – total daily usage all buildings
    total_daily = daily_df.groupby("timestamp")["kwh"].sum()
    axs[0, 0].plot(total_daily.index, total_daily.values)
    axs[0, 0].set_title("Total Daily Usage")
    axs[0, 0].set_xlabel("Date")
    axs[0, 0].set_ylabel("kWh")

    # 2. Bar chart – average daily by building
    axs[0, 1].bar(summary_df["building"], summary_df["mean"])
    axs[0, 1].set_title("Avg Daily by Building")
    axs[0, 1].set_xlabel("Building")
    axs[0, 1].set_ylabel("kWh")

    # 3. Total consumption per building
    axs[1, 0].bar(summary_df["building"], summary_df["total"])
    axs[1, 0].set_title("Total Consumption per Building")
    axs[1, 0].set_xlabel("Building")
    axs[1, 0].set_ylabel("kWh")

    # 4. You can make any other plot, here: min–max range
    axs[1, 1].bar(summary_df["building"], summary_df["max"] - summary_df["min"])
    axs[1, 1].set_title("Daily Range (max - min)")
    axs[1, 1].set_xlabel("Building")
    axs[1, 1].set_ylabel("kWh")

    plt.tight_layout()
    plt.show()   # shows dashboard with 4 subplots [web:13][web:25]


# ------------ main script ------------

if _name_ == "_main_":   # correct main block syntax [web:32][web:34]
    df = load_data()

    daily = calculate_daily_totals(df)
    weekly = calculate_weekly_aggregates(df)
    summary = building_wise_summary(df)

    manager = BuildingManager()
    for _, row in daily.iterrows():
        b = manager.get_building(row["building"])
        b.add_reading(MeterReading(row["timestamp"], row["kwh"]))

    # (optional) print one sample report
    for name, building in manager.buildings.items():
        print(building.generate_report())
        break

    create_plots(daily, summary)