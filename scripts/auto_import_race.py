#!/usr/bin/env python3
"""Auto-import latest race data - run via cron after GP"""
import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.fastf1_optimized import fastf1_service
from app.core.database import AsyncSessionLocal


# 2024 race schedule
RACES_2024 = [
    (1, "Bahrain"), (2, "Saudi Arabia"), (3, "Australia"), (4, "Japan"),
    (5, "China"), (6, "Miami"), (7, "Emilia Romagna"), (8, "Monaco"),
    (9, "Canada"), (10, "Spain"), (11, "Austria"), (12, "Great Britain"),
    (13, "Hungary"), (14, "Belgium"), (15, "Netherlands"), (16, "Italy"),
    (17, "Azerbaijan"), (18, "Singapore"), (19, "United States"),
    (20, "Mexico"), (21, "Brazil"), (22, "Las Vegas"), (23, "Qatar"),
    (24, "Abu Dhabi")
]


async def import_latest():
    """Import latest race"""
    year = 2024

    # Find next race to import (simple logic)
    async with AsyncSessionLocal() as db:
        for round_num, gp_name in RACES_2024:
            print(f"Trying {gp_name}...")
            success = await fastf1_service.import_race(db, year, round_num, gp_name)
            if success:
                print(f"✓ Imported {gp_name}")
                break


if __name__ == "__main__":
    asyncio.run(import_latest())
