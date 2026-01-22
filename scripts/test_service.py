#!/usr/bin/env python3
"""Direct service test"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.services.f1 import lap_data_service

async def test():
    async with AsyncSessionLocal() as db:
        result = await lap_data_service.get_race_laps(db, race_id=1)
        print(f"Type of result: {type(result)}")
        print(f"Type of lap_data: {type(result.lap_data)}")
        if result.lap_data:
            print(f"First item type: {type(result.lap_data[0])}")
            print(f"First item: {result.lap_data[0]}")

asyncio.run(test())
