"""CrowdSnapshot model for time-series crowd density data.

Each snapshot records a zone's occupancy at a point in time, along
with derived metrics (density percentage, average gate queue) and
sustainability estimates (energy, waste).

The crowd simulator writes a new snapshot every ~5 seconds. The ops
recommender reads recent snapshots to detect trends ("Zone X density
rising 15% in last 10 minutes — proactively open Gate Y").

This table grows fast in a long-running demo. A production system
would partition by timestamp or use a time-series database. For our
SQLite demo, periodic cleanup is sufficient.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.zone import Zone


class CrowdSnapshot(Base):
    """A point-in-time record of zone crowd density and sustainability metrics."""

    __tablename__ = "crowd_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id: Mapped[str] = mapped_column(ForeignKey("zones.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    occupancy: Mapped[int] = mapped_column(Integer)
    density_pct: Mapped[float] = mapped_column(Float)
    # occupancy / capacity * 100
    avg_gate_queue: Mapped[float] = mapped_column(Float, default=0.0)
    # Average queue length across this zone's gates

    # ── Sustainability signals ───────────────────────────────
    estimated_energy_kw: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_waste_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Relationships ────────────────────────────────────────
    zone: Mapped[Zone] = relationship(back_populates="crowd_snapshots")
