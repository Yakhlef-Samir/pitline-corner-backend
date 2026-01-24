"""F1 API endpoints - cleaned minimal version"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db_session
from app.schemas.common import ApiResponse
from app.schemas.f1 import (
    RaceResponse,
    RaceList,
    DriverResponse,
    DriverList,
    LapDataResponse,
    LapDataList,
    PitStopResponse,
    PitStopList,
)
from app.services.f1 import (
    race_service,
    driver_service,
    lap_data_service,
    pit_stop_service,
)
from app.services.fastf1_optimized import fastf1_service
from app.services.strategy import (
    pit_stop_calculator,
    overtake_calculator,
    defense_calculator,
    weather_calculator,
)

router = APIRouter()


# Race endpoints
@router.get("/races", response_model=ApiResponse[RaceList])
async def get_races(
    season: Optional[int] = Query(None, description="Filter by season year"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all F1 races"""
    try:
        races = await race_service.get_all_races(db, season=season)
        return ApiResponse(data=races)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "RACE_FETCH_ERROR", "message": str(e)}},
        )


@router.get("/races/{race_id}", response_model=ApiResponse[RaceResponse])
async def get_race(race_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get a specific race by ID"""
    try:
        race = await race_service.get_race_by_id(db, race_id)
        if not race:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {"code": "RACE_NOT_FOUND", "message": "Race not found"}
                },
            )
        return ApiResponse(data=race)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "RACE_FETCH_ERROR", "message": str(e)}},
        )


@router.get("/races/{race_id}/laps")
async def get_race_laps(
    race_id: int,
    driver_id: Optional[int] = Query(None, description="Filter by driver ID"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get lap data for a race"""
    try:
        race = await race_service.get_race_by_id(db, race_id)
        if not race:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {"code": "RACE_NOT_FOUND", "message": "Race not found"}
                },
            )

        laps = await lap_data_service.get_race_laps(
            db, race_id=race_id, driver_id=driver_id
        )
        return {
            "data": laps.model_dump(),
            "meta": {"timestamp": "2024-01-21T20:00:00Z"},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "LAP_DATA_ERROR", "message": str(e)}},
        )


@router.get("/races/{race_id}/pit-stops", response_model=ApiResponse[PitStopList])
async def get_race_pit_stops(
    race_id: int,
    driver_id: Optional[int] = Query(None, description="Filter by driver ID"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get pit stop data for a race"""
    try:
        race = await race_service.get_race_by_id(db, race_id)
        if not race:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {"code": "RACE_NOT_FOUND", "message": "Race not found"}
                },
            )

        pit_stops = await pit_stop_service.get_race_pit_stops(
            db, race_id=race_id, driver_id=driver_id
        )
        return ApiResponse(data=pit_stops)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "PIT_STOP_ERROR", "message": str(e)}},
        )


# Driver endpoints
@router.get("/drivers", response_model=ApiResponse[DriverList])
async def get_drivers(
    search: Optional[str] = Query(None, description="Search drivers by name or code"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all F1 drivers"""
    try:
        if search:
            drivers = await driver_service.search_drivers(db, query=search)
        else:
            drivers = await driver_service.get_all_drivers(db)
        return ApiResponse(data=drivers)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DRIVER_FETCH_ERROR", "message": str(e)}},
        )


@router.get("/drivers/{driver_id}", response_model=ApiResponse[DriverResponse])
async def get_driver(driver_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get a specific driver by ID"""
    try:
        driver = await driver_service.get_driver_by_id(db, driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {"code": "DRIVER_NOT_FOUND", "message": "Driver not found"}
                },
            )
        return ApiResponse(data=driver)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DRIVER_FETCH_ERROR", "message": str(e)}},
        )


# Data import endpoints
@router.post("/import/race/{season}/{round}")
async def import_race_data(
    season: int, round: int, db: AsyncSession = Depends(get_db_session)
):
    """Import race data from Fast-F1"""
    try:
        gp_names = {1: "Bahrain", 2: "Saudi Arabia", 3: "Australia", 4: "Japan"}
        gp_name = gp_names.get(round, f"Round{round}")
        success = await fastf1_service.import_race(db, season, round, gp_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "IMPORT_FAILED",
                        "message": "Failed to import race data",
                    }
                },
            )

        return ApiResponse(
            data={"message": f"Successfully imported {gp_name} {season} R{round}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "IMPORT_ERROR", "message": str(e)}},
        )


# Strategy Time Machine endpoints
@router.get("/simulations/pit-stop")
async def simulate_pit_stop_strategy(
    race_id: int = Query(..., description="Race ID"),
    driver_id: int = Query(..., description="Driver ID"),
    alternative_stop_lap: int = Query(..., description="Alternative pit stop lap"),
    db: AsyncSession = Depends(get_db_session),
):
    """Simulate alternative pit stop strategy"""
    try:
        result = await pit_stop_calculator.calculate_alternative_strategy(
            db, race_id, driver_id, alternative_stop_lap
        )
        return ApiResponse(data=result.__dict__)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_INPUT", "message": str(e)}},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "SIMULATION_ERROR", "message": str(e)}},
        )


@router.get("/simulations/overtake")
async def simulate_overtake_strategy(
    race_id: int = Query(..., description="Race ID"),
    driver_id: int = Query(..., description="Driver ID"),
    target_driver_id: int = Query(..., description="Target driver to overtake"),
    db: AsyncSession = Depends(get_db_session),
):
    """Analyze overtaking opportunities"""
    try:
        result = await overtake_calculator.analyze_overtake_opportunities(
            db, race_id, driver_id, target_driver_id
        )
        return ApiResponse(data=result.__dict__)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "SIMULATION_ERROR", "message": str(e)}},
        )


@router.get("/simulations/defend")
async def simulate_defense_strategy(
    race_id: int = Query(..., description="Race ID"),
    driver_id: int = Query(..., description="Driver ID"),
    attacking_driver_id: int = Query(..., description="Attacking driver ID"),
    db: AsyncSession = Depends(get_db_session),
):
    """Calculate defense position strategy"""
    try:
        result = await defense_calculator.calculate_defense_strategy(
            db, race_id, driver_id, attacking_driver_id
        )
        return ApiResponse(data=result.__dict__)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "SIMULATION_ERROR", "message": str(e)}},
        )


@router.get("/simulations/weather")
async def simulate_weather_strategy(
    race_id: int = Query(..., description="Race ID"),
    driver_id: int = Query(..., description="Driver ID"),
    current_weather: str = Query(..., description="Current weather"),
    expected_weather: str = Query(..., description="Expected weather"),
    db: AsyncSession = Depends(get_db_session),
):
    """Calculate weather adaptation strategy"""
    try:
        result = await weather_calculator.calculate_weather_strategy(
            db, race_id, driver_id, current_weather, expected_weather
        )
        return ApiResponse(data=result.__dict__)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "SIMULATION_ERROR", "message": str(e)}},
        )
