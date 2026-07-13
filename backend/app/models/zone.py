"""Zone model representing stadium sections.

Zones are the primary spatial unit of the stadium. Each zone has a
capacity, a live occupancy counter (updated by the crowd simulator),
and contains gates and facilities.

Design decision:
    current_occupancy is mutable live state — the crowd simulator
    updates it every tick, and the WebSocket broadcasts it. An
    alternative is to only store snapshots and derive current state,
    but for a demo that needs to feel "live," direct mutable state
    is simpler and more responsive.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.crowd_snapshot import CrowdSnapshot
    from app.models.facility import Facility
    from app.models.gate import Gate


class Zone(Base):
    """A stadium section with capacity tracking and live occupancy."""

    __tablename__ = "zones"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    name_hi: Mapped[str] = mapped_column(String(100))
    capacity: Mapped[int] = mapped_column(Integer)
    current_occupancy: Mapped[int] = mapped_column(Integer, default=0)
    zone_type: Mapped[str] = mapped_column(String(30))
    # "seating" | "concourse" | "vip" | "accessibility"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_hi: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Relationships ────────────────────────────────────────
    gates: Mapped[list[Gate]] = relationship(
        back_populates="zone", lazy="selectin"
    )
    facilities: Mapped[list[Facility]] = relationship(
        back_populates="zone", lazy="selectin"
    )
    crowd_snapshots: Mapped[list[CrowdSnapshot]] = relationship(
        back_populates="zone", lazy="noload"
    )
