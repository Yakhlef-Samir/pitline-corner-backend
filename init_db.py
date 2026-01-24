#!/usr/bin/env python3
"""
Script to initialize database tables
"""

import asyncio
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import Base, engine
from app.models import (
    Circuit,
    Driver,
    LapData,
    PitStop,
    Race,
    RaceDriver,
    Simulation,
    User,
)


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")


async def main():
    """Main function"""
    await create_tables()


if __name__ == "__main__":
    asyncio.run(main())
