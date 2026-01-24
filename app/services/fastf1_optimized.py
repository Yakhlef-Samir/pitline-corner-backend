"""Optimized Fast-F1 service with caching and async support"""

import fastf1
import asyncio
import pickle
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.f1 import Race, Driver, LapData, PitStop
import pandas as pd

from app.core.config import settings

# Enable Fast-F1 cache
import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "cache", "fastf1")
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


class FastF1Service:
    """Optimized Fast-F1 service with Redis caching"""

    def __init__(self):
        self.redis: Optional[Redis] = None
        self.cache_ttl = 86400 * 7  # 7 days for race data

    async def get_redis(self) -> Optional[Redis]:
        """Lazy Redis connection (optional)"""
        if not self.redis:
            try:
                self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=False)
                await self.redis.ping()
            except Exception as e:
                print(f"Redis unavailable: {e}")
                self.redis = None
        return self.redis

    async def _get_cached(self, key: str) -> Optional[Any]:
        """Get from Redis cache (fallback if unavailable)"""
        redis = await self.get_redis()
        if not redis:
            return None
        try:
            data = await redis.get(key)
            return pickle.loads(data) if data else None
        except:
            return None

    async def _set_cached(self, key: str, value: Any):
        """Set Redis cache (skip if unavailable)"""
        redis = await self.get_redis()
        if redis:
            try:
                await redis.setex(key, self.cache_ttl, pickle.dumps(value))
            except:
                pass

    async def load_race_session(self, year: int, gp_name: str, session_type: str = "R"):
        """Load race session with caching"""
        cache_key = f"fastf1:session:{year}:{gp_name}:{session_type}"

        # Try cache first
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        # Load from Fast-F1 (blocking, run in thread pool)
        loop = asyncio.get_event_loop()
        session = await loop.run_in_executor(
            None, lambda: fastf1.get_session(year, gp_name, session_type)
        )
        await loop.run_in_executor(None, session.load)

        # Cache result
        await self._set_cached(cache_key, session)
        return session

    async def import_race(
        self, db: AsyncSession, year: int, round_num: int, gp_name: str
    ):
        """Import race data to DB"""
        print(f"Importing {gp_name} {year} R{round_num}")

        try:
            session = await self.load_race_session(year, gp_name)

            # Get race from DB
            result = await db.execute(
                select(Race).where(Race.season == year, Race.round == round_num)
            )
            race = result.scalar_one_or_none()

            if not race:
                # Create race if it doesn't exist
                print(f"Creating race {gp_name}...")
                race = Race(
                    season=year,
                    round=round_num,
                    name=f"{gp_name} Grand Prix",
                    circuit_id=round_num,  # Use round as circuit ID (will match with pre-created circuits)
                    country=gp_name,
                    date=(
                        session.event["Session1Date"]
                        if "Session1Date" in session.event
                        else datetime.now()
                    ),
                    status="completed",
                    data_imported=False,
                )
                db.add(race)
                await db.commit()
                print(f"Created race: {race.name} (ID: {race.id})")

            # Import laps
            laps = session.laps
            for idx, lap in laps.iterrows():
                lap_data = LapData(
                    race_id=race.id,
                    driver_id=await self._get_driver_id(db, lap["Driver"]),
                    lap_number=int(lap["LapNumber"]),
                    position=int(lap["Position"]) if pd.notna(lap["Position"]) else 1,
                    lap_time_seconds=(
                        lap["LapTime"].total_seconds()
                        if pd.notna(lap["LapTime"])
                        else 0
                    ),
                    sector1_time=(
                        lap["Sector1Time"].total_seconds()
                        if pd.notna(lap["Sector1Time"])
                        else 0
                    ),
                    sector2_time=(
                        lap["Sector2Time"].total_seconds()
                        if pd.notna(lap["Sector2Time"])
                        else 0
                    ),
                    sector3_time=(
                        lap["Sector3Time"].total_seconds()
                        if pd.notna(lap["Sector3Time"])
                        else 0
                    ),
                    tire_compound=(
                        lap["Compound"] if pd.notna(lap["Compound"]) else "UNKNOWN"
                    ),
                    tire_age=int(lap["TyreLife"]) if pd.notna(lap["TyreLife"]) else 0,
                    gap_to_leader=None,
                )
                db.add(lap_data)

            await db.commit()
            print(f"OK Imported {len(laps)} laps")
            return True

        except Exception as e:
            print(f"ERROR: {e}")
            await db.rollback()
            return False

    async def _get_driver_id(self, db: AsyncSession, driver_code: str) -> int:
        """Get driver ID by code"""
        result = await db.execute(select(Driver.id).where(Driver.code == driver_code))
        driver_id = result.scalar_one_or_none()
        return driver_id if driver_id else 1  # Fallback


# Singleton
fastf1_service = FastF1Service()
