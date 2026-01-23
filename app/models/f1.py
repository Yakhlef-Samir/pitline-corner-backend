from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User


class Circuit(Base):
    """F1 Circuit information"""
    __tablename__ = "circuits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    length_km: Mapped[float] = mapped_column(Float, nullable=False)
    turns: Mapped[int] = mapped_column(Integer, nullable=False)
    track_map_data: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    races: Mapped[list["Race"]] = relationship("Race", back_populates="circuit")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )


class Race(Base):
    """F1 Race information"""
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    season: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    circuit_id: Mapped[int] = mapped_column(ForeignKey("circuits.id"), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), 
        default="scheduled", 
        nullable=False,
        index=True
    )  # scheduled, completed, cancelled
    
    # Import tracking
    data_imported: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    imported_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    
    # Relationships
    circuit: Mapped["Circuit"] = relationship("Circuit", back_populates="races")
    drivers: Mapped[list["RaceDriver"]] = relationship("RaceDriver", back_populates="race")
    lap_data: Mapped[list["LapData"]] = relationship("LapData", back_populates="race")
    pit_stops: Mapped[list["PitStop"]] = relationship("PitStop", back_populates="race")
    simulations: Mapped[list["Simulation"]] = relationship("Simulation", back_populates="race")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )


class Driver(Base):
    """F1 Driver information"""
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    driver_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    team: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Relationships
    races: Mapped[list["RaceDriver"]] = relationship("RaceDriver", back_populates="driver")
    lap_data: Mapped[list["LapData"]] = relationship("LapData", back_populates="driver")
    pit_stops: Mapped[list["PitStop"]] = relationship("PitStop", back_populates="driver")
    simulations: Mapped[list["Simulation"]] = relationship("Simulation", back_populates="driver")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )


class RaceDriver(Base):
    """Many-to-many relationship between Race and Driver"""
    __tablename__ = "race_drivers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    final_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    grid_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Relationships
    race: Mapped["Race"] = relationship("Race", back_populates="drivers")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="races")


class LapData(Base):
    """Lap timing data for each driver in each race"""
    __tablename__ = "lap_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), nullable=False, index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False, index=True)
    lap_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    lap_time_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Sector times
    sector1_time: Mapped[float] = mapped_column(Float, nullable=False)
    sector2_time: Mapped[float] = mapped_column(Float, nullable=False)
    sector3_time: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Tire information
    tire_compound: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        index=True
    )  # SOFT, MEDIUM, HARD, INTERMEDIATE, WET
    tire_age: Mapped[int] = mapped_column(Integer, nullable=False)  # laps on this tire
    
    # Gap information
    gap_to_leader: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gap_to_ahead: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationships
    race: Mapped["Race"] = relationship("Race", back_populates="lap_data")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="lap_data")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )


class PitStop(Base):
    """Pit stop data"""
    __tablename__ = "pit_stops"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), nullable=False, index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False, index=True)
    stop_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lap: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    tire_compound_before: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tire_compound_after: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Relationships
    race: Mapped["Race"] = relationship("Race", back_populates="pit_stops")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="pit_stops")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )


class Simulation(Base):
    """Strategy simulation results"""
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"), nullable=False, index=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Alternative strategy
    alternative_stop_lap: Mapped[int] = mapped_column(Integer, nullable=False)
    alternative_tire_compound: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Results
    predicted_position: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_gap: Mapped[float] = mapped_column(Float, nullable=False)
    actual_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    actual_gap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Calculated deltas
    position_delta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gap_delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Metadata
    calculation_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    traffic_affected: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    race: Mapped["Race"] = relationship("Race", back_populates="simulations")
    driver: Mapped["Driver"] = relationship("Driver", back_populates="simulations")
    user: Mapped["User"] = relationship("User")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, onupdate=datetime.utcnow
    )
