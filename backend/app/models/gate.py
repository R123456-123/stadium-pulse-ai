"""Gate model representing stadium entry/exit points.

Gates are tied to zones and track real-time queue length and status.
The crowd simulator updates queue_length every tick; the ops recommender
uses this data to suggest gate redirects when queues exceed thresholds.

capacity_per_minute represents throughput rate — how many fans can pass
through per minute under normal conditions. This drives the "ETA" calculation
in recommendations ("redirect fans to Gate 5, ETA 6 min").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.zone import Zone


class Gate(Base):
    """A stadium entry/exit point with live queue tracking."""

    __tablename__ = "gates"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    name_hi: Mapped[str] = mapped_column(String(50))
    zone_id: Mapped[str] = mapped_column(ForeignKey("zones.id"))
    gate_type: Mapped[str] = mapped_column(String(20))
    # "entry" | "exit" | "both" | "emergency"
    is_accessible: Mapped[bool] = mapped_column(Boolean, default=False)
    capacity_per_minute: Mapped[int] = mapped_column(Integer)
    current_queue_length: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="open")
    # "open" | "congested" | "closed"

    # ── Relationships ────────────────────────────────────────
    zone: Mapped[Zone] = relationship(back_populates="gates")
