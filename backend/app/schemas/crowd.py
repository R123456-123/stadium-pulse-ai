"""Crowd data schemas for WebSocket broadcast and ops dashboard.

These schemas define the real-time data structure pushed to
connected clients every simulator tick. They're separate from
the REST response schemas because the WebSocket payload has
a different shape — it's a full state snapshot with alerts
and sustainability signals, not individual entity responses.
"""

from __future__ import annotations

from pydantic import BaseModel


class GateCrowdStatus(BaseModel):
    """Per-gate live status within a crowd update."""

    gate_id: str
    name: str
    queue_length: int
    status: str
    estimated_wait_minutes: float


class ZoneCrowdStatus(BaseModel):
    """Per-zone live status within a crowd update."""

    zone_id: str
    name: str
    name_hi: str
    capacity: int
    current_occupancy: int
    density_pct: float
    zone_type: str
    gates: list[GateCrowdStatus] = []


class CrowdAlert(BaseModel):
    """An alert generated when zones exceed density thresholds."""

    zone_id: str
    zone_name: str
    level: str  # "warning" | "critical"
    message: str


class SustainabilitySummary(BaseModel):
    """Aggregated sustainability estimates across all zones."""

    total_energy_kw: float
    total_waste_kg: float
    energy_per_zone: dict[str, float] = {}
    waste_per_zone: dict[str, float] = {}


class CrowdUpdate(BaseModel):
    """Complete crowd state snapshot broadcast via WebSocket.

    This is the top-level message sent to all connected clients
    on every simulator tick (~5 seconds).
    """

    type: str = "crowd_update"
    match_minute: int
    match_phase: str
    timestamp: str
    zones: list[ZoneCrowdStatus] = []
    sustainability: SustainabilitySummary
    alerts: list[CrowdAlert] = []
