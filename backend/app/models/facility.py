"""Facility model representing stadium amenities.

Covers restrooms, first-aid stations, food & beverage outlets,
prayer rooms, baby care rooms, and lost-and-found desks. Each
facility is tied to a zone and tagged with accessibility info.

This is a key data source for the fan assistant's function calling —
when a fan asks "Where's the nearest restroom?", Gemini calls
get_nearest_facility(facility_type="restroom", current_zone=...).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.zone import Zone


class Facility(Base):
    """A stadium amenity with accessibility and localization metadata."""

    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    name_hi: Mapped[str] = mapped_column(String(100))
    zone_id: Mapped[str] = mapped_column(ForeignKey("zones.id"))
    facility_type: Mapped[str] = mapped_column(String(30))
    # "restroom" | "first_aid" | "food_beverage" | "prayer_room" | "baby_care" | "lost_found"
    is_accessible: Mapped[bool] = mapped_column(Boolean, default=False)
    floor_level: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_hi: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ────────────────────────────────────────
    zone: Mapped[Zone] = relationship(back_populates="facilities")
