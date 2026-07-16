"""Simulated crowd density engine with match-phase awareness.

Runs as an async background task during app lifespan, updating
zone occupancy and gate queues every tick (~5 seconds). The
simulator follows a realistic match-day curve:

    Pre-match (T-90 to T-0):  Gradual ramp-up
    Match start (T+0 to T+10): Spike as fans rush to seats
    First half (T+10 to T+45): Stable with small fluctuations
    Halftime (T+45 to T+60):   Redistribution (concourse spikes)
    Second half (T+60 to T+90): Stable again
    Post-match (T+90 to T+120): Rapid exit wave
    → Loops back to T-90 for continuous demo

Clearly labeled as *simulated data* in the UI and README.
No real IoT integration — this is a seeded simulator.
"""

from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import structlog
from sqlalchemy import select

from app.models.crowd_snapshot import CrowdSnapshot
from app.models.zone import Zone
from app.schemas.crowd import (
    CrowdAlert,
    CrowdUpdate,
    GateCrowdStatus,
    SustainabilitySummary,
    ZoneCrowdStatus,
)
from app.services.sustainability import estimate_energy_kw, estimate_waste_kg

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = structlog.get_logger(__name__)

# ── Match Phase Configuration ────────────────────────────────
# Target occupancy as a fraction of capacity, per zone type and phase.
# The simulator moves each zone toward its target with random noise.

PHASE_TARGETS: dict[str, dict[str, float]] = {
    "pre_early": {"seating": 0.08, "concourse": 0.12, "vip": 0.05},
    "pre_approach": {"seating": 0.30, "concourse": 0.40, "vip": 0.20},
    "pre_rush": {"seating": 0.65, "concourse": 0.50, "vip": 0.55},
    "match_start": {"seating": 0.88, "concourse": 0.18, "vip": 0.82},
    "first_half": {"seating": 0.92, "concourse": 0.12, "vip": 0.88},
    "halftime": {"seating": 0.55, "concourse": 0.72, "vip": 0.70},
    "second_half": {"seating": 0.90, "concourse": 0.15, "vip": 0.85},
    "post_match": {"seating": 0.08, "concourse": 0.35, "vip": 0.03},
}

# Speed at which occupancy moves toward target (fraction per tick)
_CONVERGENCE_RATE = 0.15
# Random noise range (fraction of capacity)
_NOISE_RANGE = 0.03

# Density thresholds for alerts
_WARNING_THRESHOLD = 75.0   # percent
_CRITICAL_THRESHOLD = 90.0  # percent

# Tick configuration
_TICK_INTERVAL_SECONDS = 5
_MINUTES_PER_TICK = 2  # Simulate 2 match minutes per real 5 seconds


def _get_match_phase(minute: int) -> str:
    """Determine the current match phase from the match minute.

    Args:
        minute: Current match minute (negative = pre-match).

    Returns:
        Phase name string matching PHASE_TARGETS keys.
    """
    if minute < -60:
        return "pre_early"
    elif minute < -15:
        return "pre_approach"
    elif minute < 0:
        return "pre_rush"
    elif minute < 10:
        return "match_start"
    elif minute < 45:
        return "first_half"
    elif minute < 60:
        return "halftime"
    elif minute < 90:
        return "second_half"
    else:
        return "post_match"


def _compute_target_occupancy(
    capacity: int, zone_type: str, phase: str
) -> int:
    """Compute the target occupancy for a zone in a given phase.

    Args:
        capacity: Maximum zone capacity.
        zone_type: Zone type (seating, concourse, vip).
        phase: Current match phase.

    Returns:
        Target occupancy count.
    """
    targets = PHASE_TARGETS.get(phase, PHASE_TARGETS["first_half"])
    target_fraction = targets.get(zone_type, 0.5)
    return int(capacity * target_fraction)


def _update_occupancy(
    current: int, target: int, capacity: int
) -> int:
    """Move current occupancy toward target with noise.

    Uses exponential smoothing (convergence rate) plus random noise
    to create realistic-looking crowd fluctuations.

    Args:
        current: Current occupancy.
        target: Target occupancy for this phase.
        capacity: Maximum capacity (clamp bound).

    Returns:
        Updated occupancy, clamped to [0, capacity].
    """
    # Move toward target
    delta = (target - current) * _CONVERGENCE_RATE

    # Add random noise
    noise = random.uniform(-_NOISE_RANGE, _NOISE_RANGE) * capacity

    new_occupancy = current + delta + noise
    return max(0, min(capacity, int(new_occupancy)))


def _compute_queue_length(
    zone_occupancy: int,
    zone_capacity: int,
    gate_throughput: int,
    gate_type: str,
    phase: str,
) -> int:
    """Compute a realistic queue length for a gate.

    Queue length scales with how busy the zone is and whether
    fans are primarily entering or exiting.

    Args:
        zone_occupancy: Current zone occupancy.
        zone_capacity: Zone capacity.
        gate_throughput: Gate throughput (people/minute).
        gate_type: "entry", "exit", "both", or "emergency".
        phase: Current match phase.

    Returns:
        Simulated queue length.
    """
    density = zone_occupancy / max(zone_capacity, 1)

    # Entering phases have higher entry gate queues
    entering_phases = {"pre_early", "pre_approach", "pre_rush", "match_start"}
    # Exiting phases have higher exit gate queues
    exiting_phases = {"post_match"}

    if phase in entering_phases and gate_type in ("entry", "both"):
        # Queue proportional to density and throughput
        base_queue = density * gate_throughput * random.uniform(0.5, 2.5)
    elif phase in exiting_phases and gate_type in ("exit", "both"):
        base_queue = density * gate_throughput * random.uniform(1.0, 3.0)
    elif gate_type == "emergency":
        base_queue = 0  # Emergency exits don't have normal queues
    else:
        base_queue = density * gate_throughput * random.uniform(0.0, 0.8)

    return max(0, int(base_queue))


def _compute_gate_status(queue_length: int, throughput: int) -> str:
    """Determine gate status from queue length.

    Args:
        queue_length: Current queue length.
        throughput: Gate throughput (people/minute).

    Returns:
        "open" if wait < 2 min, "congested" otherwise.
    """
    if throughput <= 0:
        return "closed"
    wait_minutes = queue_length / throughput
    if wait_minutes >= 2.0:
        return "congested"
    return "open"


def _generate_alerts(zones_status: list[ZoneCrowdStatus]) -> list[CrowdAlert]:
    """Generate alerts for zones exceeding density thresholds.

    Args:
        zones_status: List of current zone statuses.

    Returns:
        List of alerts for zones above warning/critical thresholds.
    """
    alerts: list[CrowdAlert] = []
    for zone in zones_status:
        if zone.density_pct >= _CRITICAL_THRESHOLD:
            alerts.append(
                CrowdAlert(
                    zone_id=zone.zone_id,
                    zone_name=zone.name,
                    level="critical",
                    message=(
                        f"{zone.name} at {zone.density_pct:.0f}% capacity — "
                        f"consider redirecting incoming fans"
                    ),
                )
            )
        elif zone.density_pct >= _WARNING_THRESHOLD:
            alerts.append(
                CrowdAlert(
                    zone_id=zone.zone_id,
                    zone_name=zone.name,
                    level="warning",
                    message=(
                        f"{zone.name} approaching capacity ({zone.density_pct:.0f}%)"
                    ),
                )
            )
    return alerts


class CrowdSimulator:
    """Async background task that simulates crowd dynamics.

    The simulator reads current state from the database, computes
    new occupancy/queue values based on the match phase, writes
    snapshots, and broadcasts the update via the provided callback.

    Usage::

        simulator = CrowdSimulator(session_factory, broadcast_fn)
        task = asyncio.create_task(simulator.run())
        # ... later ...
        simulator.stop()
        await task
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        broadcast_fn: Callable[[dict], Awaitable[None]],
    ) -> None:
        self._session_factory = session_factory
        self._broadcast = broadcast_fn
        self._running = False
        self._match_minute = -90
        self._tick_count = 0

    @property
    def match_minute(self) -> int:
        """Current simulated match minute."""
        return self._match_minute

    @property
    def match_phase(self) -> str:
        """Current match phase name."""
        return _get_match_phase(self._match_minute)

    def stop(self) -> None:
        """Signal the simulator to stop after the current tick."""
        self._running = False

    async def run(self) -> None:
        """Main loop — runs until stop() is called.

        Each iteration:
        1. Advance the match clock
        2. Update zone occupancy and gate queues
        3. Store a CrowdSnapshot per zone
        4. Build and broadcast the crowd update
        """
        self._running = True
        logger.info(
            "crowd_simulator_started",
            tick_interval=_TICK_INTERVAL_SECONDS,
            minutes_per_tick=_MINUTES_PER_TICK,
        )

        while self._running:
            try:
                await self._tick()
            except Exception:
                logger.exception("crowd_simulator_tick_error")

            await asyncio.sleep(_TICK_INTERVAL_SECONDS)

        logger.info("crowd_simulator_stopped")

    async def _tick(self) -> None:
        """Execute one simulation tick."""
        # Advance match clock
        self._match_minute += _MINUTES_PER_TICK
        if self._match_minute > 120:
            self._match_minute = -90  # Loop for continuous demo
            logger.info("crowd_simulator_loop_reset")

        phase = self.match_phase
        self._tick_count += 1

        # Accumulators for broadcast
        zones_status: list[ZoneCrowdStatus] = []
        energy_per_zone: dict[str, float] = {}
        waste_per_zone: dict[str, float] = {}

        async with self._session_factory() as session:
            # Fetch all zones with their gates (selectin loaded)
            result = await session.execute(select(Zone))
            zones = list(result.scalars().all())

            for zone in zones:
                # 1. Update zone occupancy
                target = _compute_target_occupancy(
                    zone.capacity, zone.zone_type, phase
                )
                zone.current_occupancy = _update_occupancy(
                    zone.current_occupancy, target, zone.capacity
                )

                # 2. Update gate queues
                gate_statuses: list[GateCrowdStatus] = []
                for gate in zone.gates:
                    gate.current_queue_length = _compute_queue_length(
                        zone.current_occupancy,
                        zone.capacity,
                        gate.capacity_per_minute,
                        gate.gate_type,
                        phase,
                    )
                    gate.status = _compute_gate_status(
                        gate.current_queue_length, gate.capacity_per_minute
                    )
                    gate_statuses.append(
                        GateCrowdStatus(
                            gate_id=gate.id,
                            name=gate.name,
                            queue_length=gate.current_queue_length,
                            status=gate.status,
                            estimated_wait_minutes=round(
                                gate.current_queue_length
                                / max(gate.capacity_per_minute, 1),
                                1,
                            ),
                        )
                    )

                # 3. Compute density and sustainability
                density_pct = round(
                    (zone.current_occupancy / max(zone.capacity, 1)) * 100, 1
                )
                energy = estimate_energy_kw(zone.current_occupancy, zone.zone_type)
                waste = estimate_waste_kg(
                    zone.current_occupancy, _TICK_INTERVAL_SECONDS
                )

                energy_per_zone[zone.id] = energy
                waste_per_zone[zone.id] = waste

                # 4. Store snapshot
                avg_queue = (
                    sum(g.current_queue_length for g in zone.gates)
                    / max(len(zone.gates), 1)
                )
                snapshot = CrowdSnapshot(
                    zone_id=zone.id,
                    occupancy=zone.current_occupancy,
                    density_pct=density_pct,
                    avg_gate_queue=round(avg_queue, 1),
                    estimated_energy_kw=energy,
                    estimated_waste_kg=waste,
                )
                session.add(snapshot)

                # 5. Build zone status for broadcast
                zones_status.append(
                    ZoneCrowdStatus(
                        zone_id=zone.id,
                        name=zone.name,
                        name_hi=zone.name_hi,
                        capacity=zone.capacity,
                        current_occupancy=zone.current_occupancy,
                        density_pct=density_pct,
                        zone_type=zone.zone_type,
                        gates=gate_statuses,
                    )
                )

            await session.commit()

        # 6. Generate alerts and broadcast
        alerts = _generate_alerts(zones_status)
        update = CrowdUpdate(
            match_minute=self._match_minute,
            match_phase=phase,
            timestamp=datetime.now(timezone.utc).isoformat(),
            zones=zones_status,
            sustainability=SustainabilitySummary(
                total_energy_kw=round(sum(energy_per_zone.values()), 2),
                total_waste_kg=round(sum(waste_per_zone.values()), 3),
                energy_per_zone=energy_per_zone,
                waste_per_zone=waste_per_zone,
            ),
            alerts=alerts,
        )

        await self._broadcast(update.model_dump())

        # Log every 10th tick to avoid noise
        if self._tick_count % 10 == 0:
            total_occ = sum(z.current_occupancy for z in zones_status)
            logger.info(
                "crowd_simulator_tick",
                match_minute=self._match_minute,
                phase=phase,
                total_occupancy=total_occ,
                alert_count=len(alerts),
            )
