#!/usr/bin/env python3
"""
Prototype script to test parsing TracingInsights RaceData CSV files
This validates the data structure and mapping before full integration
"""

from datetime import datetime
from pathlib import Path

import pandas as pd


def parse_races_csv(csv_path: str):
    """Parse races.csv and show structure"""
    print("=" * 80)
    print("PARSING RACES.CSV")
    print("=" * 80)

    df = pd.read_csv(csv_path)

    # Show column structure
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"Total races: {len(df)}")

    # Filter 2024 races
    df_2024 = df[df["year"] == 2024]
    print(f"\n2024 Races: {len(df_2024)}")

    # Show sample race
    print("\nSample 2024 race:")
    sample = df_2024.iloc[0]
    print(f"  raceId: {sample['raceId']}")
    print(f"  year: {sample['year']}")
    print(f"  round: {sample['round']}")
    print(f"  name: {sample['name']}")
    print(f"  date: {sample['date']}")
    print(f"  circuitId: {sample['circuitId']}")

    return df


def parse_drivers_csv(csv_path: str):
    """Parse drivers.csv and show structure"""
    print("\n" + "=" * 80)
    print("PARSING DRIVERS.CSV")
    print("=" * 80)

    df = pd.read_csv(csv_path)

    # Show column structure
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"Total drivers: {len(df)}")

    # Show sample drivers
    print("\nSample drivers:")
    for idx, row in df.head(5).iterrows():
        print(
            f"  {row['code']}: {row['forename']} {row['surname']} (#{row['number'] if pd.notna(row['number']) else 'N/A'})"
        )

    return df


def parse_lap_times_csv(csv_path: str):
    """Parse lap_times.csv and show structure"""
    print("\n" + "=" * 80)
    print("PARSING LAP_TIMES.CSV")
    print("=" * 80)

    df = pd.read_csv(csv_path)

    # Show column structure
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"Total lap records: {len(df)}")

    # Get sample race (first raceId)
    sample_race_id = df["raceId"].iloc[0]
    df_sample = df[df["raceId"] == sample_race_id].head(10)

    print(f"\nSample laps (raceId={sample_race_id}):")
    for idx, row in df_sample.iterrows():
        print(
            f"  Lap {row['lap']}: Driver {row['driverId']}, Position {row['position']}, "
            f"Time: {row['time']} ({row['milliseconds']}ms)"
        )

    return df


def parse_pit_stops_csv(csv_path: str):
    """Parse pit_stops.csv and show structure"""
    print("\n" + "=" * 80)
    print("PARSING PIT_STOPS.CSV")
    print("=" * 80)

    df = pd.read_csv(csv_path)

    # Show column structure
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"Total pit stops: {len(df)}")

    # Get sample race (first raceId)
    sample_race_id = df["raceId"].iloc[0]
    df_sample = df[df["raceId"] == sample_race_id].head(10)

    print(f"\nSample pit stops (raceId={sample_race_id}):")
    for idx, row in df_sample.iterrows():
        print(
            f"  Stop {row['stop']}: Driver {row['driverId']}, Lap {row['lap']}, "
            f"Duration: {row['duration']}s ({row['milliseconds']}ms)"
        )

    return df


def analyze_data_mapping():
    """Analyze mapping between RaceData CSV and our DB schema"""
    print("\n" + "=" * 80)
    print("DATA MAPPING ANALYSIS")
    print("=" * 80)

    mapping = {
        "races.csv": {
            "raceId": "Race.id (primary key)",
            "year": "Race.season",
            "round": "Race.round",
            "name": "Race.name",
            "date": "Race.date (datetime)",
            "circuitId": "Race.circuit_id (FK -> circuits)",
            "time": "Race time component (merge with date)",
        },
        "drivers.csv": {
            "driverId": "Driver.id (primary key)",
            "number": "Driver.driver_number",
            "code": "Driver.code (3 chars)",
            "forename": "Driver.first_name",
            "surname": "Driver.last_name",
            "nationality": "Driver.country",
        },
        "lap_times.csv": {
            "raceId": "LapData.race_id (FK)",
            "driverId": "LapData.driver_id (FK)",
            "lap": "LapData.lap_number",
            "position": "LapData.position",
            "milliseconds": "LapData.lap_time_seconds (convert ms->seconds)",
        },
        "pit_stops.csv": {
            "raceId": "PitStop.race_id (FK)",
            "driverId": "PitStop.driver_id (FK)",
            "stop": "PitStop.stop_number",
            "lap": "PitStop.lap",
            "milliseconds": "PitStop.duration_seconds (convert ms->seconds)",
        },
    }

    print("\nMapping RaceData CSV -> Database Schema:\n")
    for file, fields in mapping.items():
        print(f"{file}:")
        for csv_field, db_field in fields.items():
            print(f"  {csv_field:20} -> {db_field}")
        print()


def identify_missing_data():
    """Identify what data is missing in RaceData vs what we need"""
    print("\n" + "=" * 80)
    print("MISSING DATA ANALYSIS")
    print("=" * 80)

    missing = {
        "LapData": [
            "sector1_time (sector times not in lap_times.csv)",
            "sector2_time",
            "sector3_time",
            "tire_compound (SOFT/MEDIUM/HARD - not in RaceData)",
            "tire_age (laps on tire - not in RaceData)",
            "gap_to_leader (not in lap_times.csv)",
            "gap_to_ahead (not in lap_times.csv)",
        ],
        "PitStop": [
            "tire_compound_before (not in pit_stops.csv)",
            "tire_compound_after (not in pit_stops.csv)",
        ],
        "Circuit": [
            "length_km (circuits.csv may have this)",
            "turns (circuits.csv may have this)",
            "track_map_data (not available)",
        ],
        "Driver": [
            "team (need to get from constructors/results)",
        ],
    }

    print("\nData fields MISSING in RaceData (needed for full MVP):\n")
    for model, fields in missing.items():
        print(f"{model}:")
        for field in fields:
            print(f"  X {field}")
        print()

    print("\nRECOMMENDATION:")
    print("  RaceData provides BASIC race data (races, drivers, lap times, pit stops)")
    print(
        "  For TELEMETRY (sector times, tire data), we need TracingInsights-Archive/*"
    )
    print("  -> Use HYBRID approach:")
    print("     - RaceData for races/drivers/basic lap times")
    print("     - TracingInsights-Archive JSON for telemetry/tire/sector data")


def main():
    """Run all parsing tests"""
    data_dir = Path(__file__).parent.parent / "data_samples"

    print("TracingInsights RaceData CSV Parsing Prototype")
    print("=" * 80)
    print(f"Data directory: {data_dir}")
    print()

    # Parse each CSV
    races_df = parse_races_csv(data_dir / "races.csv")
    drivers_df = parse_drivers_csv(data_dir / "drivers.csv")
    lap_times_df = parse_lap_times_csv(data_dir / "lap_times.csv")
    pit_stops_df = parse_pit_stops_csv(data_dir / "pit_stops.csv")

    # Analyze mapping
    analyze_data_mapping()

    # Identify missing data
    identify_missing_data()

    print("\n" + "=" * 80)
    print("PROTOTYPE PARSING COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Download circuits.csv to get track details")
    print("  2. Test parsing TracingInsights-Archive JSON for telemetry")
    print("  3. Create TracingInsightsService with both CSV + JSON support")
    print("  4. Implement data transformations to match DB schema")


if __name__ == "__main__":
    main()
