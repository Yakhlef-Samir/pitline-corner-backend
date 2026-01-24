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
    print("Importing F1 circuits...")

    try:
        import fastf1

        # Get 2024 season schedule
        schedule = fastf1.get_event_schedule(2024)
        circuits_added = 0

        # Filter for actual races (where Session5 exists - race day)
        races = schedule[schedule['Session5Date'].notna()]

        for _, event in races.iterrows():
            # Location is the circuit identifier in FastF1
            location = event.get("Location")
            country = event.get("Country")
            event_name = event.get("EventName")

            if not (location and country):
                continue

            # Check if circuit already exists
            existing = await circuit_repo.get_by_name(db, name=location)
            if existing:
                continue

            # Create circuit
            circuit_data = {
                "name": location,
                "country": country,
                "length_km": 5.0,  # Default length - will be updated later
                "turns": 15,  # Default turns - will be updated later
            }

            new_circuit = await circuit_repo.create(db, obj_in=circuit_data)
            circuits_added += 1
            print(f"  Added circuit: {location} ({country})")

        print(f"Imported {circuits_added} circuits")
        return circuits_added

    except (ImportError, Exception) as e:
        print(f"FastF1 not available or error occurred ({type(e).__name__}), creating mock circuits...")
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
            {"name": "Monaco", "country": "Monaco", "length_km": 3.337, "turns": 19},
            {"name": "Silverstone", "country": "United Kingdom", "length_km": 5.891, "turns": 18},
        ]

        circuits_added = 0
        for circuit_data in mock_circuits:
            existing = await circuit_repo.get_by_name(db, name=circuit_data["name"])
            if not existing:
                await circuit_repo.create(db, obj_in=circuit_data)
                circuits_added += 1
                print(f"  Added mock circuit: {circuit_data['name']}")

        print(f"Imported {circuits_added} mock circuits")
        return circuits_added


async def import_drivers(db: AsyncSession):
    """Import F1 drivers from 2024 season"""
    print("Importing F1 drivers...")

    try:
        import fastf1

        # Get drivers from first race of 2024
        session = fastf1.get_session(2024, 1, "R")
        session.load()

        drivers_added = 0
        # session.drivers is a list of driver numbers
        for driver_number in session.drivers:
            # Get driver details from the session
            driver = session.drivers[driver_number]

            # Check if driver already exists
            existing = await driver_repo.get_by_number(db, driver_number=driver_number)
            if existing:
                continue

            # Extract driver information
            driver_code = driver.get("Code", f"DRV{driver_number}")
            first_name = driver.get("FirstName", "Unknown")
            last_name = driver.get("LastName", "Driver")
            team_name = driver.get("TeamName", "Unknown Team")
            country_code = driver.get("CountryCode", None)

            # Create driver
            driver_data = {
                "driver_number": int(driver_number),
                "code": driver_code,
                "first_name": first_name,
                "last_name": last_name,
                "team": team_name,
                "country": country_code,
            }

            new_driver = await driver_repo.create(db, obj_in=driver_data)
            drivers_added += 1
            print(f"  Added driver: {first_name} {last_name} ({driver_code})")

        print(f"Imported {drivers_added} drivers from FastF1")
        return drivers_added

    except (ImportError, Exception) as e:
        print(f"FastF1 not available or error occurred ({type(e).__name__}), creating mock drivers...")
        # Create mock drivers for testing - 2024 F1 Season grid
        mock_drivers = [
            {
                "driver_number": 1,
                "code": "VER",
                "first_name": "Max",
                "last_name": "Verstappen",
                "team": "Red Bull Racing",
                "country": "NED",
            },
            {
                "driver_number": 11,
                "code": "PER",
                "first_name": "Sergio",
                "last_name": "Pérez",
                "team": "Red Bull Racing",
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
            {
                "driver_number": 3,
                "code": "ALO",
                "first_name": "Fernando",
                "last_name": "Alonso",
                "team": "Aston Martin",
                "country": "ESP",
            },
            {
                "driver_number": 14,
                "code": "STR",
                "first_name": "Lance",
                "last_name": "Stroll",
                "team": "Aston Martin",
                "country": "CAN",
            },
            {
                "driver_number": 27,
                "code": "HUL",
                "first_name": "Nico",
                "last_name": "Hulkenberg",
                "team": "Haas",
                "country": "GER",
            },
            {
                "driver_number": 20,
                "code": "MAG",
                "first_name": "Kevin",
                "last_name": "Magnussen",
                "team": "Haas",
                "country": "DEN",
            },
            {
                "driver_number": 10,
                "code": "GAS",
                "first_name": "Pierre",
                "last_name": "Gasly",
                "team": "Alpine",
                "country": "FRA",
            },
            {
                "driver_number": 31,
                "code": "OCO",
                "first_name": "Esteban",
                "last_name": "Ocon",
                "team": "Alpine",
                "country": "FRA",
            },
            {
                "driver_number": 18,
                "code": "TSU",
                "first_name": "Yuki",
                "last_name": "Tsunoda",
                "team": "Racing Bulls",
                "country": "JPN",
            },
            {
                "driver_number": 22,
                "code": "LAW",
                "first_name": "Daniel",
                "last_name": "Lawson",
                "team": "Racing Bulls",
                "country": "NZL",
            },
            {
                "driver_number": 24,
                "code": "ZHO",
                "first_name": "Zhou",
                "last_name": "Guanyu",
                "team": "Kick Sauber",
                "country": "CHN",
            },
            {
                "driver_number": 2,
                "code": "BOT",
                "first_name": "Valtteri",
                "last_name": "Bottas",
                "team": "Kick Sauber",
                "country": "FIN",
            },
            {
                "driver_number": 77,
                "code": "VET",
                "first_name": "Sebastian",
                "last_name": "Vettel",
                "team": "Aston Martin",
                "country": "GER",
            },
            {
                "driver_number": 12,
                "code": "RIC",
                "first_name": "Daniel",
                "last_name": "Ricciardo",
                "team": "Racing Bulls",
                "country": "AUS",
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
                    f"  Added mock driver: {driver_data['first_name']} {driver_data['last_name']} ({driver_data['code']})"
                )

        print(f"Imported {drivers_added} mock drivers")
        return drivers_added


async def import_races(db: AsyncSession):
    """Import F1 races from 2024 season"""
    print("Importing F1 races...")

    try:
        import fastf1

        # Get 2024 season schedule
        schedule = fastf1.get_event_schedule(2024)
        races_added = 0

        # Filter for actual races (where Session5 exists - race day)
        races = schedule[schedule['Session5Date'].notna()]

        for _, event in races.iterrows():
            round_number = event.get("RoundNumber")
            race_date = event.get("Session5Date")
            event_name = event.get("EventName")
            location = event.get("Location")
            country = event.get("Country")

            if not (round_number and race_date and event_name):
                continue

            # Check if race already exists
            existing_races = await race_repo.get_by_season(db, season=2024)
            if any(r.round == round_number for r in existing_races):
                continue

            # Find circuit by location (which is the circuit identifier in FastF1)
            circuit_obj = await circuit_repo.get_by_name(db, name=location)
            if not circuit_obj:
                print(f"  Circuit not found: {location}, skipping race")
                continue

            # Create race
            race_data = {
                "season": 2024,
                "round": int(round_number),
                "name": event_name,
                "circuit_id": circuit_obj.id,
                "country": country,
                "date": race_date,
                "status": "scheduled",
            }

            new_race = await race_repo.create(db, obj_in=race_data)
            races_added += 1
            print(f"  Added race: {event_name} (Round {round_number})")

        print(f"Imported {races_added} races from FastF1")
        return races_added

    except (ImportError, Exception) as e:
        print(f"FastF1 not available or error occurred ({type(e).__name__}), creating mock races...")
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
                f"  Added mock race: {race_data['name']} (Round {race_data['round']})"
            )

        print(f"Imported {races_added} mock races")
        return races_added


async def main():
    """Main import function"""
    print("Starting F1 data import...")

    async with AsyncSessionLocal() as db:
        try:
            # Import data
            circuits_count = await import_circuits(db)
            drivers_count = await import_drivers(db)
            races_count = await import_races(db)

            await db.commit()

            print("\nImport completed!")
            print(f"   Circuits: {circuits_count}")
            print(f"   Drivers: {drivers_count}")
            print(f"   Races: {races_count}")

        except Exception as e:
            await db.rollback()
            print(f"Import failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
