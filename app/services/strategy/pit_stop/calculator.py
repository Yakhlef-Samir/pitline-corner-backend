"""
Pit Stop Strategy Calculator
Calculates how position changes with different pit stop lap numbers
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.f1 import LapData, PitStop
from app.repositories.f1 import lap_data, pit_stop


@dataclass
class LapMetrics:
    """Metrics for a single lap"""

    lap_number: int
    lap_time: float
    position: int
    gap_to_leader: Optional[float]
    tire_compound: str
    tire_age: int


@dataclass
class PitStopSimulation:
    """Result of a pit stop simulation"""

    driver_id: int
    race_id: int
    scenario_name: str
    original_stop_lap: int
    alternative_stop_lap: int
    original_position_final: int
    alternative_position_final: int
    position_gain: int
    time_loss_at_stop: float
    time_gain_after_stop: float
    confidence_score: float
    recommendation: str
    detailed_analysis: Dict[str, Any]


class PitStopStrategyCalculator:
    """
    Calculates pit stop strategy alternatives using real race data.

    Simple calculation logic:
    1. Get actual lap times and positions from race
    2. When pit stop happens:
       - Driver loses ~20 seconds (pit stop duration)
       - Driver might lose 5+ positions if traffic during stop
       - But gets fresh tires = faster lap times after
    3. Calculate final position with alternative stop lap
    """

    async def calculate_alternative_strategy(
        self, db: AsyncSession, race_id: int, driver_id: int, alternative_stop_lap: int
    ) -> PitStopSimulation:
        """
        Calculate how position changes with different pit stop lap.

        Args:
            race_id: ID of the race
            driver_id: ID of the driver
            alternative_stop_lap: Lap number for alternative pit stop

        Returns:
            PitStopSimulation with results
        """
        # Get all lap data for this driver
        driver_laps = await lap_data.get_driver_laps(db, race_id, driver_id)
        if not driver_laps:
            raise ValueError(
                f"No lap data found for driver {driver_id} in race {race_id}"
            )

        # Get actual pit stops
        actual_pit_stops = await pit_stop.get_driver_pit_stops(db, race_id, driver_id)

        # Find original pit stop lap
        original_stop_lap = actual_pit_stops[0].lap if actual_pit_stops else None

        # Calculate metrics at different points
        original_final_position = self._get_position_at_lap(
            driver_laps, len(driver_laps)
        )

        # Simulate alternative strategy
        alternative_final_position = await self._simulate_position_after_stop(
            driver_laps, alternative_stop_lap, len(driver_laps)
        )

        position_gain = original_final_position - alternative_final_position

        # Estimate time metrics
        time_loss_at_stop = self._estimate_pit_stop_loss(
            driver_laps, alternative_stop_lap
        )
        time_gain_after_stop = self._estimate_fresh_tire_gain(
            driver_laps, alternative_stop_lap
        )

        # Calculate confidence (0-100)
        confidence_score = self._calculate_confidence(
            position_gain, time_loss_at_stop, time_gain_after_stop
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(
            position_gain, original_stop_lap, alternative_stop_lap, confidence_score
        )

        return PitStopSimulation(
            driver_id=driver_id,
            race_id=race_id,
            scenario_name="Pit Stop Strategy",
            original_stop_lap=original_stop_lap or 0,
            alternative_stop_lap=alternative_stop_lap,
            original_position_final=original_final_position,
            alternative_position_final=alternative_final_position,
            position_gain=position_gain,
            time_loss_at_stop=time_loss_at_stop,
            time_gain_after_stop=time_gain_after_stop,
            confidence_score=confidence_score,
            recommendation=recommendation,
            detailed_analysis={
                "total_laps": len(driver_laps),
                "original_tire_strategy": (
                    self._analyze_tire_strategy(driver_laps, original_stop_lap)
                    if original_stop_lap
                    else "Unknown"
                ),
                "alternative_tire_strategy": self._analyze_tire_strategy(
                    driver_laps, alternative_stop_lap
                ),
                "tire_degradation": self._analyze_tire_degradation(driver_laps),
                "competitive_context": "Lahir simulation vs 1 pit stop leader",
            },
        )

    def _get_position_at_lap(self, lap_data: List[Any], target_lap: int) -> int:
        """Get position at specific lap number"""
        for lap in reversed(lap_data):
            if lap.lap_number <= target_lap:
                return lap.position
        return lap_data[0].position if lap_data else 20

    async def _simulate_position_after_stop(
        self, lap_data: List[Any], stop_lap: int, total_laps: int
    ) -> int:
        """
        Simulate position after pit stop.

        Logic:
        - At stop lap: lose 20 seconds (pit duration) = lose positions
        - After stop: fresh tires = 2-3% faster = gain time back
        - Net result: usually gain 1-3 positions on field
        """
        position_at_stop = self._get_position_at_lap(lap_data, stop_lap)

        # Simulate pit stop impact: typically lose 1-2 positions due to time loss
        position_after_stop = min(position_at_stop + 2, 20)

        # Fresh tires = faster lap times for next 15-20 laps
        # This helps regain positions
        position_gain_from_fresh_tires = 1

        final_position = max(position_after_stop - position_gain_from_fresh_tires, 1)

        return final_position

    def _estimate_pit_stop_loss(self, lap_data: List[Any], stop_lap: int) -> float:
        """Estimate time loss from pit stop"""
        # Standard pit stop = 20-22 seconds
        # Plus time lost in pit lane
        avg_lap_time = sum(lap.lap_time_seconds for lap in lap_data) / len(lap_data)
        return 22.0 + (avg_lap_time * 0.15)  # 15% pit lane time

    def _estimate_fresh_tire_gain(self, lap_data: List[Any], stop_lap: int) -> float:
        """Estimate time gain from fresh tires"""
        # Fresh tires = 2-3% faster for 10-15 laps
        avg_lap_time = sum(lap.lap_time_seconds for lap in lap_data) / len(lap_data)
        fresh_tire_gain = avg_lap_time * 0.025  # 2.5% improvement
        laps_with_gain = 15
        return fresh_tire_gain * laps_with_gain

    def _calculate_confidence(
        self, position_gain: int, time_loss: float, time_gain: float
    ) -> float:
        """Calculate confidence score (0-100)"""
        # More position gain = higher confidence
        position_confidence = min(position_gain * 25, 100)

        # Time metrics confidence
        time_confidence = (time_gain / time_loss * 100) if time_loss > 0 else 50

        # Average them
        confidence = (position_confidence + time_confidence) / 2
        return min(confidence, 100)

    def _generate_recommendation(
        self,
        position_gain: int,
        original_stop_lap: int,
        alternative_stop_lap: int,
        confidence_score: float,
    ) -> str:
        """Generate text recommendation"""
        if position_gain > 0:
            return (
                f"Pit stop at lap {alternative_stop_lap} could gain {position_gain} positions "
                f"(confidence: {confidence_score:.0f}%). Recommended timing."
            )
        elif position_gain == 0:
            return (
                f"Pit stop at lap {alternative_stop_lap} offers similar results "
                f"to current strategy. Consider race circumstances."
            )
        else:
            return (
                f"Pit stop at lap {alternative_stop_lap} could cost {abs(position_gain)} positions. "
                f"Current strategy preferred."
            )

    def _analyze_tire_strategy(self, lap_data: List[Any], stop_lap: int) -> str:
        """Analyze tire strategy before/after stop"""
        before_stop = [lap for lap in lap_data if lap.lap_number <= stop_lap]
        after_stop = [lap for lap in lap_data if lap.lap_number > stop_lap]

        before_compound = before_stop[-1].tire_compound if before_stop else "Unknown"
        after_compound = after_stop[0].tire_compound if after_stop else "Unknown"

        return f"{before_compound} → {after_compound}"

    def _analyze_tire_degradation(self, lap_data: List[Any]) -> Dict[str, float]:
        """Analyze tire degradation throughout race"""
        if not lap_data or len(lap_data) < 2:
            return {}

        first_lap_time = lap_data[0].lap_time_seconds
        last_lap_time = lap_data[-1].lap_time_seconds
        degradation = last_lap_time - first_lap_time
        degradation_percentage = (degradation / first_lap_time) * 100

        return {
            "first_lap_time": first_lap_time,
            "last_lap_time": last_lap_time,
            "degradation_seconds": degradation,
            "degradation_percentage": degradation_percentage,
        }


# Singleton instance
pit_stop_calculator = PitStopStrategyCalculator()
