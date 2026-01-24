"""F1 service layer - cleaned and optimized"""

from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.f1 import driver, lap_data, pit_stop, race
from app.schemas.f1 import (
    DriverList,
    DriverResponse,
    LapDataList,
    LapDataResponse,
    PitStopList,
    PitStopResponse,
    RaceList,
    RaceResponse,
)


class RaceService:
    """Service layer for race business logic"""

    @staticmethod
    async def get_all_races(db: AsyncSession, season: Optional[int] = None) -> RaceList:
        """Get all races, optionally filtered by season"""
        if season:
            races = await race.get_by_season(db, season=season)
        else:
            races = await race.get_multi(db, limit=1000)

        # Convert to response schema
        race_responses = []
        for race_obj in races:
            race_data = {
                "id": race_obj.id,
                "season": race_obj.season,
                "round": race_obj.round,
                "name": race_obj.name,
                "circuit_id": race_obj.circuit_id,
                "country": race_obj.country,
                "date": race_obj.date,
                "status": race_obj.status,
                "data_imported": race_obj.data_imported,
                "imported_at": race_obj.imported_at,
                "created_at": race_obj.created_at,
                "updated_at": race_obj.updated_at,
                "circuit": None,
            }
            race_responses.append(RaceResponse(**race_data))

        return RaceList(races=race_responses)

    @staticmethod
    async def get_race_by_id(db: AsyncSession, race_id: int) -> Optional[RaceResponse]:
        """Get a specific race by ID"""
        return await race.get_with_circuit(db, race_id)


class DriverService:
    """Service layer for driver business logic"""

    @staticmethod
    async def get_all_drivers(db: AsyncSession) -> DriverList:
        """Get all drivers"""
        drivers = await driver.get_multi(db, limit=1000)
        return DriverList(drivers=drivers)

    @staticmethod
    async def get_driver_by_id(
        db: AsyncSession, driver_id: int
    ) -> Optional[DriverResponse]:
        """Get a specific driver by ID"""
        return await driver.get(db, id=driver_id)

    @staticmethod
    async def search_drivers(
        db: AsyncSession, query: str, limit: int = 10
    ) -> DriverList:
        """Search drivers by name or code"""
        drivers = await driver.search_drivers(db, query=query, limit=limit)
        return DriverList(drivers=drivers)


class LapDataService:
    """Service layer for lap data business logic"""

    @staticmethod
    def _transform_lap_to_response(lap: Any) -> LapDataResponse:
        """Transform database LapData model to response schema"""
        from app.schemas.f1 import SectorTimes

        lap_dict = {
            "id": lap.id,
            "race_id": lap.race_id,
            "driver_id": lap.driver_id,
            "lap_number": lap.lap_number,
            "position": lap.position,
            "lap_time_seconds": lap.lap_time_seconds,
            "sector_times": SectorTimes(
                sector1=lap.sector1_time,
                sector2=lap.sector2_time,
                sector3=lap.sector3_time,
            ),
            "tire_compound": lap.tire_compound,
            "tire_age": lap.tire_age,
            "gap_to_leader": lap.gap_to_leader,
            "gap_to_ahead": lap.gap_to_ahead,
            "driver": lap.driver if hasattr(lap, "driver") else None,
            "created_at": lap.created_at,
            "updated_at": lap.updated_at,
        }
        return LapDataResponse(**lap_dict)

    @staticmethod
    async def get_race_laps(
        db: AsyncSession, race_id: int, driver_id: Optional[int] = None
    ) -> LapDataList:
        """Get lap data for a race, optionally filtered by driver"""
        laps = await lap_data.get_race_laps(db, race_id=race_id, driver_id=driver_id)
        lap_responses = [LapDataService._transform_lap_to_response(lap) for lap in laps]
        return LapDataList(lap_data=lap_responses)


class PitStopService:
    """Service layer for pit stop business logic"""

    @staticmethod
    async def get_race_pit_stops(
        db: AsyncSession, race_id: int, driver_id: Optional[int] = None
    ) -> PitStopList:
        """Get pit stops for a race, optionally filtered by driver"""
        pit_stops = await pit_stop.get_race_pit_stops(
            db, race_id=race_id, driver_id=driver_id
        )
        return PitStopList(pit_stops=pit_stops)


# Service instances
race_service = RaceService()
driver_service = DriverService()
lap_data_service = LapDataService()
pit_stop_service = PitStopService()
