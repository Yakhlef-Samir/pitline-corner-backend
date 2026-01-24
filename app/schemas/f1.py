from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal


# Base schemas
class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}


class TimestampedSchema(BaseSchema):
    created_at: datetime
    updated_at: Optional[datetime]


# Circuit schemas
class CircuitBase(BaseSchema):
    name: str = Field(..., description="Circuit name")
    country: str = Field(..., description="Country where circuit is located")
    length_km: float = Field(..., description="Circuit length in kilometers")
    turns: int = Field(..., description="Number of turns in the circuit")
    track_map_data: Optional[str] = Field(
        None, description="Track map data (JSON or base64)"
    )


class CircuitCreate(CircuitBase):
    pass


class CircuitResponse(CircuitBase, TimestampedSchema):
    id: int


class CircuitList(BaseSchema):
    circuits: List[CircuitResponse]


# Driver schemas
class DriverBase(BaseSchema):
    driver_number: int = Field(..., description="Driver's permanent number")
    code: str = Field(..., max_length=3, description="Driver's 3-letter code")
    first_name: str = Field(..., description="Driver's first name")
    last_name: str = Field(..., description="Driver's last name")
    team: str = Field(..., description="Driver's current team")
    country: Optional[str] = Field(None, description="Driver's nationality")


class DriverCreate(DriverBase):
    pass


class DriverResponse(DriverBase, TimestampedSchema):
    id: int


class DriverList(BaseSchema):
    drivers: List[DriverResponse]


# Race schemas
TireCompound = Literal["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
RaceStatus = Literal["scheduled", "completed", "cancelled"]


class RaceBase(BaseSchema):
    season: int = Field(..., description="F1 season year")
    round: int = Field(..., description="Race round number in the season")
    name: str = Field(..., description="Race name")
    circuit_id: int = Field(..., description="Circuit ID")
    country: str = Field(..., description="Country where race takes place")
    date: datetime = Field(..., description="Race date and time")
    status: RaceStatus = Field(default="scheduled", description="Race status")


class RaceCreate(RaceBase):
    pass


class RaceResponse(RaceBase, TimestampedSchema):
    id: int
    circuit: Optional[CircuitResponse] = None
    data_imported: bool
    imported_at: Optional[datetime]


class RaceList(BaseSchema):
    races: List[RaceResponse]


# RaceDriver schemas (many-to-many)
class RaceDriverBase(BaseSchema):
    final_position: Optional[int] = Field(None, description="Final finishing position")
    grid_position: Optional[int] = Field(None, description="Starting grid position")
    status: Optional[str] = Field(
        None, description="Driver status (finished, retired, etc.)"
    )


class RaceDriverResponse(RaceDriverBase, TimestampedSchema):
    id: int
    race_id: int
    driver_id: int
    driver: Optional[DriverResponse] = None


# LapData schemas
class SectorTimes(BaseSchema):
    sector1: float = Field(..., description="Sector 1 time in seconds")
    sector2: float = Field(..., description="Sector 2 time in seconds")
    sector3: float = Field(..., description="Sector 3 time in seconds")


class LapDataBase(BaseSchema):
    lap_number: int = Field(..., description="Lap number")
    position: int = Field(..., description="Position at end of lap")
    lap_time_seconds: float = Field(..., description="Total lap time in seconds")
    sector_times: SectorTimes = Field(..., description="Individual sector times")
    tire_compound: TireCompound = Field(..., description="Tire compound used")
    tire_age: int = Field(..., description="Number of laps on this tire")
    gap_to_leader: Optional[float] = Field(
        None, description="Gap to race leader in seconds"
    )
    gap_to_ahead: Optional[float] = Field(
        None, description="Gap to car ahead in seconds"
    )


class LapDataCreate(LapDataBase):
    race_id: int
    driver_id: int


class LapDataResponse(TimestampedSchema):
    id: int
    race_id: int
    driver_id: int
    lap_number: int
    position: int
    lap_time_seconds: float
    sector_times: SectorTimes
    tire_compound: TireCompound
    tire_age: int
    gap_to_leader: Optional[float] = None
    gap_to_ahead: Optional[float] = None
    driver: Optional[DriverResponse] = None


class LapDataList(BaseSchema):
    lap_data: List[LapDataResponse]


# PitStop schemas
class PitStopBase(BaseSchema):
    stop_number: int = Field(..., description="Pit stop number")
    lap: int = Field(..., description="Lap number when pit stop occurred")
    duration_seconds: float = Field(..., description="Pit stop duration in seconds")
    tire_compound_before: Optional[TireCompound] = Field(
        None, description="Tire compound before stop"
    )
    tire_compound_after: TireCompound = Field(
        ..., description="Tire compound after stop"
    )


class PitStopCreate(PitStopBase):
    race_id: int
    driver_id: int


class PitStopResponse(PitStopBase, TimestampedSchema):
    id: int
    race_id: int
    driver_id: int
    driver: Optional[DriverResponse] = None


class PitStopList(BaseSchema):
    pit_stops: List[PitStopResponse]


# Simulation schemas
class SimulationRequest(BaseSchema):
    race_id: int = Field(..., description="Race ID for simulation")
    driver_id: int = Field(..., description="Driver ID for simulation")
    alternative_stop_lap: int = Field(..., description="Alternative pit stop lap")
    alternative_tire_compound: TireCompound = Field(
        ..., description="Alternative tire compound"
    )


class SimulationMetadata(BaseSchema):
    calculation_time_ms: int = Field(
        ..., description="Time taken for calculation in milliseconds"
    )
    traffic_affected: bool = Field(
        ..., description="Whether traffic affected the simulation"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score of prediction"
    )


class SimulationResult(BaseSchema):
    predicted_position: int = Field(..., description="Predicted finishing position")
    predicted_gap: float = Field(..., description="Predicted gap to winner in seconds")
    actual_position: Optional[int] = Field(
        None, description="Actual finishing position (if race completed)"
    )
    actual_gap: Optional[float] = Field(
        None, description="Actual gap to winner (if race completed)"
    )
    position_delta: Optional[int] = Field(None, description="Position change vs actual")
    gap_delta: Optional[float] = Field(
        None, description="Gap change vs actual in seconds"
    )
    metadata: SimulationMetadata = Field(..., description="Simulation metadata")


class SimulationCreate(SimulationRequest):
    pass


class SimulationResponse(SimulationRequest, TimestampedSchema):
    id: int
    user_id: int
    result: SimulationResult
    race: Optional[RaceResponse] = None
    driver: Optional[DriverResponse] = None


class SimulationList(BaseSchema):
    simulations: List[SimulationResponse]


# Season schemas
class SeasonBase(BaseSchema):
    year: int = Field(..., description="Season year")
    total_races: int = Field(..., description="Total number of races in the season")
    completed_races: int = Field(default=0, description="Number of completed races")


class SeasonCreate(SeasonBase):
    pass


class SeasonResponse(SeasonBase, TimestampedSchema):
    id: int


class SeasonList(BaseSchema):
    seasons: List[SeasonResponse]


# Full race data with all related information
class RaceFullData(BaseSchema):
    race: RaceResponse
    drivers: List[DriverResponse]
    lap_data: List[LapDataResponse]
    pit_stops: List[PitStopResponse]
