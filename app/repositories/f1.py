from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.f1 import (
    Circuit,
    Driver,
    LapData,
    PitStop,
    Race,
    RaceDriver,
    Simulation,
)
from app.repositories.base import CRUDBase
from app.schemas.f1 import CircuitCreate, DriverCreate, RaceCreate, SimulationCreate


class CRUDCircuit(CRUDBase[Circuit, CircuitCreate, dict]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Circuit]:
        """Get circuit by name"""
        result = await db.execute(select(Circuit).where(Circuit.name == name))
        return result.scalar_one_or_none()

    async def get_by_country(self, db: AsyncSession, *, country: str) -> List[Circuit]:
        """Get all circuits in a country"""
        result = await db.execute(select(Circuit).where(Circuit.country == country))
        return result.scalars().all()


class CRUDRace(CRUDBase[Race, RaceCreate, dict]):
    async def get_by_season(self, db: AsyncSession, *, season: int) -> List[Race]:
        """Get all races in a season"""
        result = await db.execute(
            select(Race).where(Race.season == season).order_by(Race.round)
        )
        return result.scalars().all()

    async def get_by_status(self, db: AsyncSession, *, status: str) -> List[Race]:
        """Get races by status"""
        result = await db.execute(select(Race).where(Race.status == status))
        return result.scalars().all()

    async def get_with_circuit(self, db: AsyncSession, race_id: int) -> Optional[Race]:
        """Get race with circuit information"""
        result = await db.execute(
            select(Race).options(selectinload(Race.circuit)).where(Race.id == race_id)
        )
        return result.scalar_one_or_none()

    async def get_imported_races(self, db: AsyncSession) -> List[Race]:
        """Get all races with imported data"""
        result = await db.execute(select(Race).where(Race.data_imported == True))
        return result.scalars().all()


class CRUDDriver(CRUDBase[Driver, DriverCreate, dict]):
    async def get_by_number(
        self, db: AsyncSession, *, driver_number: int
    ) -> Optional[Driver]:
        """Get driver by permanent number"""
        result = await db.execute(
            select(Driver).where(Driver.driver_number == driver_number)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[Driver]:
        """Get driver by 3-letter code"""
        result = await db.execute(select(Driver).where(Driver.code == code.upper()))
        return result.scalar_one_or_none()

    async def get_by_team(self, db: AsyncSession, *, team: str) -> List[Driver]:
        """Get all drivers in a team"""
        result = await db.execute(select(Driver).where(Driver.team == team))
        return result.scalars().all()

    async def search_drivers(
        self, db: AsyncSession, *, query: str, limit: int = 10
    ) -> List[Driver]:
        """Search drivers by name or code"""
        search_pattern = f"%{query}%"
        result = await db.execute(
            select(Driver)
            .where(
                or_(
                    Driver.first_name.ilike(search_pattern),
                    Driver.last_name.ilike(search_pattern),
                    Driver.code.ilike(search_pattern),
                )
            )
            .limit(limit)
        )
        return result.scalars().all()


class CRUDRaceDriver(CRUDBase[RaceDriver, dict, dict]):
    async def get_race_drivers(
        self, db: AsyncSession, race_id: int
    ) -> List[RaceDriver]:
        """Get all drivers in a race"""
        result = await db.execute(
            select(RaceDriver)
            .options(selectinload(RaceDriver.driver))
            .where(RaceDriver.race_id == race_id)
            .order_by(RaceDriver.final_position)
        )
        return result.scalars().all()

    async def get_driver_races(
        self, db: AsyncSession, driver_id: int
    ) -> List[RaceDriver]:
        """Get all races for a driver"""
        result = await db.execute(
            select(RaceDriver)
            .options(selectinload(RaceDriver.race))
            .where(RaceDriver.driver_id == driver_id)
        )
        return result.scalars().all()


class CRUDLapData(CRUDBase[LapData, dict, dict]):
    async def get_race_laps(
        self, db: AsyncSession, race_id: int, driver_id: Optional[int] = None
    ) -> List[LapData]:
        """Get lap data for a race, optionally filtered by driver"""
        query = (
            select(LapData)
            .options(selectinload(LapData.driver))
            .where(LapData.race_id == race_id)
        )
        if driver_id:
            query = query.where(LapData.driver_id == driver_id)

        query = query.order_by(LapData.driver_id, LapData.lap_number)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_driver_laps(
        self, db: AsyncSession, race_id: int, driver_id: int
    ) -> List[LapData]:
        """Get all laps for a specific driver in a race"""
        result = await db.execute(
            select(LapData)
            .options(selectinload(LapData.driver))
            .where(and_(LapData.race_id == race_id, LapData.driver_id == driver_id))
            .order_by(LapData.lap_number)
        )
        return result.scalars().all()

    async def get_fastest_lap(
        self, db: AsyncSession, race_id: int, driver_id: Optional[int] = None
    ) -> Optional[LapData]:
        """Get fastest lap in a race, optionally for a specific driver"""
        query = (
            select(LapData)
            .options(selectinload(LapData.driver))
            .where(LapData.race_id == race_id)
        )
        if driver_id:
            query = query.where(LapData.driver_id == driver_id)

        query = query.order_by(LapData.lap_time_seconds).limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_lap_by_number(
        self, db: AsyncSession, race_id: int, driver_id: int, lap_number: int
    ) -> Optional[LapData]:
        """Get specific lap data"""
        result = await db.execute(
            select(LapData)
            .options(selectinload(LapData.driver))
            .where(
                and_(
                    LapData.race_id == race_id,
                    LapData.driver_id == driver_id,
                    LapData.lap_number == lap_number,
                )
            )
        )
        return result.scalar_one_or_none()


class CRUDPitStop(CRUDBase[PitStop, dict, dict]):
    async def get_race_pit_stops(
        self, db: AsyncSession, race_id: int, driver_id: Optional[int] = None
    ) -> List[PitStop]:
        """Get pit stops for a race, optionally filtered by driver"""
        query = select(PitStop).where(PitStop.race_id == race_id)
        if driver_id:
            query = query.where(PitStop.driver_id == driver_id)

        query = query.order_by(PitStop.lap)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_driver_pit_stops(
        self, db: AsyncSession, race_id: int, driver_id: int
    ) -> List[PitStop]:
        """Get all pit stops for a specific driver in a race"""
        result = await db.execute(
            select(PitStop)
            .where(and_(PitStop.race_id == race_id, PitStop.driver_id == driver_id))
            .order_by(PitStop.lap)
        )
        return result.scalars().all()


class CRUDSimulation(CRUDBase[Simulation, SimulationCreate, dict]):
    async def get_user_simulations(
        self, db: AsyncSession, user_id: int, race_id: Optional[int] = None
    ) -> List[Simulation]:
        """Get simulations for a user, optionally filtered by race"""
        query = select(Simulation).where(Simulation.user_id == user_id)
        if race_id:
            query = query.where(Simulation.race_id == race_id)

        query = query.order_by(Simulation.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_race_simulations(
        self, db: AsyncSession, race_id: int, driver_id: Optional[int] = None
    ) -> List[Simulation]:
        """Get simulations for a race, optionally filtered by driver"""
        query = select(Simulation).where(Simulation.race_id == race_id)
        if driver_id:
            query = query.where(Simulation.driver_id == driver_id)

        query = query.order_by(Simulation.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    async def get_driver_simulations(
        self, db: AsyncSession, race_id: int, driver_id: int
    ) -> List[Simulation]:
        """Get all simulations for a specific driver in a race"""
        result = await db.execute(
            select(Simulation)
            .where(
                and_(Simulation.race_id == race_id, Simulation.driver_id == driver_id)
            )
            .order_by(Simulation.created_at.desc())
        )
        return result.scalars().all()

    async def get_simulation_with_results(
        self, db: AsyncSession, simulation_id: int
    ) -> Optional[Simulation]:
        """Get simulation with full race and driver data"""
        result = await db.execute(
            select(Simulation)
            .options(
                selectinload(Simulation.race),
                selectinload(Simulation.driver),
                selectinload(Simulation.user),
            )
            .where(Simulation.id == simulation_id)
        )
        return result.scalar_one_or_none()


# Create singleton instances
circuit = CRUDCircuit(Circuit)
race = CRUDRace(Race)
driver = CRUDDriver(Driver)
race_driver = CRUDRaceDriver(RaceDriver)
lap_data = CRUDLapData(LapData)
pit_stop = CRUDPitStop(PitStop)
simulation = CRUDSimulation(Simulation)
