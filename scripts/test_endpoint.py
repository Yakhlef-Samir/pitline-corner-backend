#!/usr/bin/env python3
"""Test lap data endpoint"""

import asyncio
import httpx


async def test():
    async with httpx.AsyncClient() as client:
        # Test without driver filter first
        r = await client.get("http://localhost:8000/api/v1/races/1/laps")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Success! Got {len(data.get('data', {}).get('lap_data', []))} laps")
            if data.get("data", {}).get("lap_data"):
                first_lap = data["data"]["lap_data"][0]
                print(
                    f"First lap: Lap {first_lap['lap_number']}, Driver {first_lap['driver_id']}, Time {first_lap['lap_time_seconds']}s"
                )
                print(f"Sector times: {first_lap.get('sector_times')}")
        else:
            print(f"Error: {r.text[:500]}")


asyncio.run(test())
