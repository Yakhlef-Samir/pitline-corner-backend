#!/usr/bin/env python3
"""Quick test - import 1 race"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.fastf1_optimized import fastf1_service
from app.core.database import AsyncSessionLocal


async def test():
    async with AsyncSessionLocal() as db:
        # Test Bahrain 2024
        success = await fastf1_service.import_race(db, 2024, 1, "Bahrain")
        print("Success!" if success else "Failed")


asyncio.run(test())
