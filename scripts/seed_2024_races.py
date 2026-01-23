#!/usr/bin/env python3
"""Seed 2024 F1 races into database"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.f1 import Race, Circuit
from app.repositories.f1 import race as race_repo, circuit as circuit_repo


RACES_2024 = [
    (1, "Bahrain", 2024, 1, "Bahrain Grand Prix", "2024-03-02T15:00:00"),
    (2, "Saudi Arabia", 2024, 2, "Saudi Arabian Grand Prix", "2024-03-09T15:00:00"),
    (3, "Australia", 2024, 3, "Australian Grand Prix", "2024-03-24T06:00:00"),
    (4, "Japan", 2024, 4, "Japanese Grand Prix", "2024-04-07T06:00:00"),
    (5, "China", 2024, 5, "Chinese Grand Prix", "2024-04-21T08:00:00"),
    (6, "Miami", 2024, 6, "Miami Grand Prix", "2024-05-05T16:00:00"),
    (7, "Emilia Romagna", 2024, 7, "Emilia Romagna Grand Prix", "2024-05-19T13:00:00"),
    (8, "Monaco", 2024, 8, "Monaco Grand Prix", "2024-05-26T14:00:00"),
    (9, "Canada", 2024, 9, "Canadian Grand Prix", "2024-06-09T19:00:00"),
    (10, "Spain", 2024, 10, "Spanish Grand Prix", "2024-06-23T15:00:00"),
    (11, "Austria", 2024, 11, "Austrian Grand Prix", "2024-06-30T15:00:00"),
    (12, "Great Britain", 2024, 12, "British Grand Prix", "2024-07-07T14:00:00"),
    (13, "Hungary", 2024, 13, "Hungarian Grand Prix", "2024-07-21T13:00:00"),
    (14, "Belgium", 2024, 14, "Belgian Grand Prix", "2024-07-28T15:00:00"),
    (15, "Netherlands", 2024, 15, "Dutch Grand Prix", "2024-08-25T15:00:00"),
    (16, "Italy", 2024, 16, "Italian Grand Prix", "2024-09-01T14:00:00"),
    (17, "Azerbaijan", 2024, 17, "Azerbaijan Grand Prix", "2024-09-15T13:00:00"),
    (18, "Singapore", 2024, 18, "Singapore Grand Prix", "2024-09-22T19:00:00"),
    (19, "United States", 2024, 19, "United States Grand Prix", "2024-10-20T19:00:00"),
    (20, "Mexico", 2024, 20, "Mexico City Grand Prix", "2024-10-27T18:00:00"),
    (21, "Brazil", 2024, 21, "Brazilian Grand Prix", "2024-11-03T16:00:00"),
    (22, "Las Vegas", 2024, 22, "Las Vegas Grand Prix", "2024-11-23T22:00:00"),
    (23, "Qatar", 2024, 23, "Qatar Grand Prix", "2024-11-01T18:00:00"),
    (24, "Abu Dhabi", 2024, 24, "Abu Dhabi Grand Prix", "2024-12-08T13:00:00"),
]


async def seed_races():
    """Add all 2024 F1 races to database"""
    async with AsyncSessionLocal() as db:
        # Check existing
        existing_races = await race_repo.get_multi(db, limit=30)
        existing_rounds = {r.round for r in existing_races}
        print(f"Existing races: {len(existing_races)}")
        print(f"Existing rounds: {sorted(existing_rounds)}\n")

        # Add missing races
        count = 0
        for circuit_id, circuit_name, season, round_num, race_name, race_date in RACES_2024:
            if round_num in existing_rounds:
                print(f"[SKIP] Round {round_num}: {race_name} (already exists)")
                continue

            try:
                # Parse date
                date_obj = datetime.fromisoformat(race_date)

                # Create race
                new_race = Race(
                    season=season,
                    round=round_num,
                    name=race_name,
                    circuit_id=circuit_id,
                    country=circuit_name,
                    date=date_obj,
                    status="completed" if round_num <= 3 else "scheduled",
                    data_imported=False
                )

                db.add(new_race)
                await db.commit()

                print(f"[ADD] Round {round_num}: {race_name}")
                count += 1

            except Exception as e:
                await db.rollback()
                print(f"[ERROR] Round {round_num}: {str(e)[:50]}")

        print(f"\nAdded {count} new races")
        print(f"Total races now: {len(existing_races) + count}")


if __name__ == "__main__":
    asyncio.run(seed_races())
