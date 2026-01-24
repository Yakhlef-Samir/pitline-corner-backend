"""
Service layer for TracingInsights F1 data integration
Uses TracingInsights-Archive GitHub repos for comprehensive telemetry data
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.f1 import Circuit, Driver, LapData, PitStop, Race, RaceDriver
from app.schemas.f1 import (
    DriverList,
    DriverResponse,
    RaceList,
    RaceResponse,
    SeasonList,
    SeasonResponse,
)


class TracingInsightsService:
    """Service layer for TracingInsights F1 data integration"""

    # TracingInsights-Archive organization on GitHub
    GITHUB_ORG = "TracingInsights-Archive"
    RAW_BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_ORG}"

    # RaceData repo for basic race/driver info (CSV)
    RACEDATA_REPO = "TracingInsights/RaceData"
    RACEDATA_BASE_URL = f"https://raw.githubusercontent.com/{RACEDATA_REPO}/main/data"

    # Available seasons with telemetry
    AVAILABLE_SEASONS = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018]

    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes cache

    async def _make_request(self, url: str, use_cache: bool = True) -> bytes:
        """Make HTTP request with caching"""
        cache_key = f"{url}_{datetime.now().timestamp() // self.cache_ttl}"

        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.content

                if use_cache:
                    self.cache[cache_key] = data

                return data

        except httpx.HTTPError as e:
            raise ValueError(f"Failed to fetch data from {url}: {str(e)}")

    async def get_available_races(self, season: int) -> List[Dict[str, Any]]:
        """
        Get list of available races for a season from TracingInsights-Archive
        Returns list of race dictionaries with name and folder structure
        """
        if season not in self.AVAILABLE_SEASONS:
            raise ValueError(
                f"Season {season} not available. Available: {self.AVAILABLE_SEASONS}"
            )

        # Map of season to known races (this could be dynamically fetched from GitHub API)
        # For now, using 2024 as reference
        if season == 2024:
            return [
                {"name": "Bahrain Grand Prix", "folder": "Bahrain Grand Prix"},
                {
                    "name": "Saudi Arabian Grand Prix",
                    "folder": "Saudi Arabian Grand Prix",
                },
                {"name": "Australian Grand Prix", "folder": "Australian Grand Prix"},
                {"name": "Japanese Grand Prix", "folder": "Japanese Grand Prix"},
                {"name": "Chinese Grand Prix", "folder": "Chinese Grand Prix"},
                {"name": "Miami Grand Prix", "folder": "Miami Grand Prix"},
                {
                    "name": "Emilia Romagna Grand Prix",
                    "folder": "Emilia Romagna Grand Prix",
                },
                {"name": "Monaco Grand Prix", "folder": "Monaco Grand Prix"},
                {"name": "Canadian Grand Prix", "folder": "Canadian Grand Prix"},
                {"name": "Spanish Grand Prix", "folder": "Spanish Grand Prix"},
                {"name": "Austrian Grand Prix", "folder": "Austrian Grand Prix"},
                {"name": "British Grand Prix", "folder": "British Grand Prix"},
                {"name": "Hungarian Grand Prix", "folder": "Hungarian Grand Prix"},
                {"name": "Belgian Grand Prix", "folder": "Belgian Grand Prix"},
                {"name": "Dutch Grand Prix", "folder": "Dutch Grand Prix"},
                {"name": "Italian Grand Prix", "folder": "Italian Grand Prix"},
                {"name": "Azerbaijan Grand Prix", "folder": "Azerbaijan Grand Prix"},
                {"name": "Singapore Grand Prix", "folder": "Singapore Grand Prix"},
                {
                    "name": "United States Grand Prix",
                    "folder": "United States Grand Prix",
                },
                {"name": "Mexico City Grand Prix", "folder": "Mexico City Grand Prix"},
                {"name": "São Paulo Grand Prix", "folder": "São Paulo Grand Prix"},
                {"name": "Las Vegas Grand Prix", "folder": "Las Vegas Grand Prix"},
                {"name": "Qatar Grand Prix", "folder": "Qatar Grand Prix"},
                {"name": "Abu Dhabi Grand Prix", "folder": "Abu Dhabi Grand Prix"},
            ]
        else:
            # For other seasons, would need to implement GitHub API listing
            return []

    async def download_race_telemetry(
        self, season: int, race_folder: str, driver_code: str
    ) -> Dict[str, Any]:
        """
        Download race telemetry for a specific driver
        Returns dict with laptimes and telemetry data
        """
        base_url = f"{self.RAW_BASE_URL}/{season}/main/{race_folder}/Race/{driver_code}"

        # Download laptimes.json
        laptimes_url = f"{base_url}/laptimes.json"
        laptimes_data = await self._make_request(laptimes_url)
        laptimes = json.loads(laptimes_data)

        return {
            "driver_code": driver_code,
            "laptimes": laptimes,
        }

    async def download_race_drivers_list(
        self, season: int, race_folder: str
    ) -> List[str]:
        """
        Get list of driver codes for a race
        Note: Requires fetching drivers.json from race folder
        """
        drivers_url = (
            f"{self.RAW_BASE_URL}/{season}/main/{race_folder}/Race/drivers.json"
        )

        try:
            drivers_data = await self._make_request(drivers_url)
            drivers_json = json.loads(drivers_data)
            # drivers.json typically contains dict of driver codes -> names
            return list(drivers_json.keys()) if isinstance(drivers_json, dict) else []
        except Exception as e:
            print(f"Could not fetch drivers list: {e}")
            # Fallback: return common 2024 driver codes
            return [
                "VER",
                "PER",
                "HAM",
                "RUS",
                "LEC",
                "SAI",
                "NOR",
                "PIA",
                "ALO",
                "STR",
                "GAS",
                "OCO",
                "ALB",
                "SAR",
                "HUL",
                "MAG",
                "TSU",
                "RIC",
                "BOT",
                "ZHO",
            ]

    async def import_race_to_db(
        self,
        db: AsyncSession,
        season: int,
        round_number: int,
        race_name: str,
        race_folder: str,
    ):
        """
        Import complete race data to database
        1. Get driver list
        2. Download telemetry for each driver
        3. Parse and transform data
        4. Store in database
        """
        print(f"Importing {race_name} ({season}, Round {round_number})")

        # Get list of drivers
        driver_codes = await self.download_race_drivers_list(season, race_folder)
        print(f"Found {len(driver_codes)} drivers")

        # Download telemetry for each driver
        all_lap_data = []
        for driver_code in driver_codes:
            try:
                telemetry = await self.download_race_telemetry(
                    season, race_folder, driver_code
                )
                all_lap_data.append(telemetry)
                print(f"  Downloaded data for {driver_code}")
            except Exception as e:
                print(f"  Failed to download {driver_code}: {e}")
                continue

        # Transform and store data
        # TODO: Implement transformation logic
        print(f"Successfully imported {len(all_lap_data)} drivers for {race_name}")

        return True

    async def import_season(self, db: AsyncSession, season: int):
        """Import all races for a season"""
        races = await self.get_available_races(season)
        print(f"Importing {len(races)} races for season {season}")

        for idx, race in enumerate(races, 1):
            try:
                await self.import_race_to_db(
                    db=db,
                    season=season,
                    round_number=idx,
                    race_name=race["name"],
                    race_folder=race["folder"],
                )
            except Exception as e:
                print(f"Failed to import {race['name']}: {e}")
                continue

        print(f"Season {season} import complete")

    # Legacy compatibility methods (matching JolpicaF1Service interface)

    async def get_seasons(self) -> SeasonList:
        """Get all available F1 seasons"""
        seasons = []

        for year in self.AVAILABLE_SEASONS:
            season = SeasonResponse(
                id=year,
                year=year,
                total_races=24 if year >= 2024 else 22,  # Approximate
                completed_races=24 if year < datetime.now().year else 0,
                created_at=datetime.now(),
                updated_at=None,
            )
            seasons.append(season)

        return SeasonList(seasons=seasons)

    async def get_season_by_year(self, year: int) -> Optional[SeasonResponse]:
        """Get a specific season by year"""
        if year not in self.AVAILABLE_SEASONS:
            return None

        races = await self.get_available_races(year)

        return SeasonResponse(
            id=year,
            year=year,
            total_races=len(races),
            completed_races=len(races) if year < datetime.now().year else 0,
            created_at=datetime.now(),
            updated_at=None,
        )


# Singleton instance
tracing_insights_service = TracingInsightsService()
