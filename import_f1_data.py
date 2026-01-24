#!/usr/bin/env python3
"""
Script to import initial F1 data using FastF1
This script will:
1. Import circuits from the 2024 season
2. Import drivers from the 2024 season
3. Import basic race information
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.f1 import Circuit, Driver, Race
from app.repositories.f1 import circuit as circuit_repo
from app.repositories.f1 import driver as driver_repo
from app.repositories.f1 import race as race_repo


async def import_circuits(db: AsyncSession):
    """Import F1 circuits from 2024 season"""
    print("🏁 Importing F1 circuits...")

    try:
        import fastf1

        # Get 2024 season schedule
        schedule = fastf1.get_event_schedule(2024)
        circuits_added = 0

        for _, event in schedule.iterrows():
            if event["EventName"] and event["Location"]:
                # Check if circuit already exists
                existing = await circuit_repo.get_by_name(
                    db, name=event["CircuitShortName"]
                )
                if existing:
                    continue

                # Create circuit
                circuit_data = {
                    "name": event["CircuitShortName"],
                    "country": event["Location"],
                    "length_km": 5.0,  # Default length - will be updated later
                    "turns": 15,  # Default turns - will be updated later
                }

                new_circuit = await circuit_repo.create(db, obj_in=circuit_data)
                circuits_added += 1
                print(f"  ✅ Added circuit: {event['CircuitShortName']}")

        print(f"🏁 Imported {circuits_added} circuits")
        return circuits_added

    except ImportError:
        print("❌ FastF1 not available, creating mock circuits...")
        # Create mock circuits for testing
        mock_circuits = [
            {"name": "Bahrain", "country": "Bahrain", "length_km": 5.412, "turns": 15},
            {
                "name": "Jeddah",
                "country": "Saudi Arabia",
                "length_km": 6.174,
                "turns": 27,
            },
            {
                "name": "Albert Park",
                "country": "Australia",
                "length_km": 5.278,
                "turns": 14,
            },
            {"name": "Suzuka", "country": "Japan", "length_km": 5.807, "turns": 18},
            {"name": "Shanghai", "country": "China", "length_km": 5.451, "turns": 16},
        ]

        circuits_added = 0
        for circuit_data in mock_circuits:
            existing = await circuit_repo.get_by_name(db, name=circuit_data["name"])
            if not existing:
                await circuit_repo.create(db, obj_in=circuit_data)
                circuits_added += 1
                print(f"  ✅ Added mock circuit: {circuit_data['name']}")

        print(f"🏁 Imported {circuits_added} mock circuits")
        return circuits_added


async def import_drivers(db: AsyncSession):
    """Import F1 drivers from 2024 season"""
    print("👨‍🚒 Importing F1 drivers...")

    try:
        import fastf1

        # Get drivers from first race of 2024
        session = fastf1.get_session(2024, 1, "R")
        session.load()

        drivers_added = 0
        for driver_info in session.drivers:
            # Get driver details
            driver = session.drivers[driver_info]

            # Check if driver already exists
            existing = await driver_repo.get_by_number(
                db, driver_number=driver_info["DriverNumber"]
            )
            if existing:
                continue

            # Create driver
            driver_data = {
                "driver_number": int(driver_info["DriverNumber"]),
                "code": driver_info["Code"],
                "first_name": driver_info["FirstName"],
                "last_name": driver_info["LastName"],
                "team": driver_info["TeamName"],
                "country": driver_info.get("CountryCode", None),
            }

            new_driver = await driver_repo.create(db, obj_in=driver_data)
            drivers_added += 1
            print(
                f"  ✅ Added driver: {driver_info['FirstName']} {driver_info['LastName']} ({driver_info['Code']})"
            )

        print(f"👨‍🚒 Imported {drivers_added} drivers")
        return drivers_added

    except ImportError:
        print("❌ FastF1 not available, creating mock drivers...")
        # Create mock drivers for testing
        mock_drivers = [
            {
                "driver_number": 1,
                "code": "VER",
                "first_name": "Max",
                "last_name": "Verstappen",
                "team": "Red Bull",
                "country": "NED",
            },
            {
                "driver_number": 11,
                "code": "PER",
                "first_name": "Sergio",
                "last_name": "Perez",
                "team": "Red Bull",
                "country": "MEX",
            },
            {
                "driver_number": 16,
                "code": "LEC",
                "first_name": "Charles",
                "last_name": "Leclerc",
                "team": "Ferrari",
                "country": "MON",
            },
            {
                "driver_number": 55,
                "code": "SAI",
                "first_name": "Carlos",
                "last_name": "Sainz",
                "team": "Ferrari",
                "country": "ESP",
            },
            {
                "driver_number": 4,
                "code": "NOR",
                "first_name": "Lando",
                "last_name": "Norris",
                "team": "McLaren",
                "country": "GBR",
            },
            {
                "driver_number": 81,
                "code": "PIA",
                "first_name": "Oscar",
                "last_name": "Piastri",
                "team": "McLaren",
                "country": "AUS",
            },
            {
                "driver_number": 44,
                "code": "HAM",
                "first_name": "Lewis",
                "last_name": "Hamilton",
                "team": "Mercedes",
                "country": "GBR",
            },
            {
                "driver_number": 63,
                "code": "RUS",
                "first_name": "George",
                "last_name": "Russell",
                "team": "Mercedes",
                "country": "GBR",
            },
        ]

        drivers_added = 0
        for driver_data in mock_drivers:
            existing = await driver_repo.get_by_number(
                db, driver_number=driver_data["driver_number"]
            )
            if not existing:
                await driver_repo.create(db, obj_in=driver_data)
                drivers_added += 1
                print(
                    f"  ✅ Added mock driver: {driver_data['first_name']} {driver_data['last_name']} ({driver_data['code']})"
                )

        print(f"👨‍🚒 Imported {drivers_added} mock drivers")
        return drivers_added


async def import_races(db: AsyncSession):
    """Import F1 races from 2024 season"""
    print("🏆 Importing F1 races...")

    try:
        import fastf1

        # Get 2024 season schedule
        schedule = fastf1.get_event_schedule(2024)
        races_added = 0

        for _, event in schedule.iterrows():
            if event["RoundNumber"] and event["Session5Date"]:  # Race round and date
                # Check if race already exists
                existing_races = await race_repo.get_by_season(db, season=2024)
                if any(r.round == event["RoundNumber"] for r in existing_races):
                    continue

                # Find circuit
                circuit_obj = await circuit_repo.get_by_name(
                    db, name=event["CircuitShortName"]
                )
                if not circuit_obj:
                    print(
                        f"  ⚠️  Circuit not found: {event['CircuitShortName']}, skipping race"
                    )
                    continue

                # Create race
                race_data = {
                    "season": 2024,
                    "round": int(event["RoundNumber"]),
                    "name": event["EventName"],
                    "circuit_id": circuit_obj.id,
                    "country": event["Location"],
                    "date": event["Session5Date"],
                    "status": "scheduled",
                }

                new_race = await race_repo.create(db, obj_in=race_data)
                races_added += 1
                print(
                    f"  ✅ Added race: {event['EventName']} (Round {event['RoundNumber']})"
                )

        print(f"🏆 Imported {races_added} races")
        return races_added

    except ImportError:
        print("❌ FastF1 not available, creating mock races...")
        # Create mock races for testing
        mock_races = [
            {
                "season": 2024,
                "round": 1,
                "name": "Bahrain Grand Prix",
                "circuit_name": "Bahrain",
                "country": "Bahrain",
                "date": datetime.fromisoformat("2024-03-02T15:00:00"),
                "status": "completed",
            },
            {
                "season": 2024,
                "round": 2,
                "name": "Saudi Arabian Grand Prix",
                "circuit_name": "Jeddah",
                "country": "Saudi Arabia",
                "date": datetime.fromisoformat("2024-03-09T15:00:00"),
                "status": "completed",
            },
            {
                "season": 2024,
                "round": 3,
                "name": "Australian Grand Prix",
                "circuit_name": "Albert Park",
                "country": "Australia",
                "date": datetime.fromisoformat("2024-03-24T06:00:00"),
                "status": "completed",
            },
        ]

        races_added = 0
        for race_data in mock_races:
            # Find circuit
            circuit_obj = await circuit_repo.get_by_name(
                db, name=race_data["circuit_name"]
            )
            if not circuit_obj:
                print(
                    f"  ⚠️  Circuit not found: {race_data['circuit_name']}, skipping race"
                )
                continue

            # Remove circuit_name from race_data
            race_data_clean = {
                k: v for k, v in race_data.items() if k != "circuit_name"
            }
            race_data_clean["circuit_id"] = circuit_obj.id

            # Check if race already exists
            existing_races = await race_repo.get_by_season(db, season=2024)
            if any(r.round == race_data_clean["round"] for r in existing_races):
                continue

            await race_repo.create(db, obj_in=race_data_clean)
            races_added += 1
            print(
                f"  ✅ Added mock race: {race_data['name']} (Round {race_data['round']})"
            )

        print(f"🏆 Imported {races_added} mock races")
        return races_added


async def main():
    """Main import function"""
    print("🚀 Starting F1 data import...")

    async with AsyncSessionLocal() as db:
        try:
            # Import data
            circuits_count = await import_circuits(db)
            drivers_count = await import_drivers(db)
            races_count = await import_races(db)

            await db.commit()

            print("\n🎉 Import completed!")
            print(f"   🏁 Circuits: {circuits_count}")
            print(f"   👨‍🚒 Drivers: {drivers_count}")
            print(f"   🏆 Races: {races_count}")

        except Exception as e:
            await db.rollback()
            print(f"❌ Import failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
