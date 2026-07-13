"""Transport model representing travel options to/from the stadium.

Covers metro, bus, taxi/rideshare, and parking. Each option is
linked to the nearest gate and includes walk-time estimates and
accessibility notes.

This grounds the fan assistant's transport answers in real data
instead of generic "take the metro" responses.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TransportOption(Base):
    """A travel option to/from the stadium with accessibility details."""

    __tablename__ = "transport_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    name_hi: Mapped[str] = mapped_column(String(100))
    transport_type: Mapped[str] = mapped_column(String(20))
    # "metro" | "bus" | "taxi" | "rideshare" | "parking"
    nearest_gate_id: Mapped[str | None] = mapped_column(
        ForeignKey("gates.id"), nullable=True
    )
    estimated_walk_minutes: Mapped[int] = mapped_column(Integer)
    accessibility_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    accessibility_notes_hi: Mapped[str | None] = mapped_column(Text, nullable=True)
    schedule_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    schedule_info_hi: Mapped[str | None] = mapped_column(Text, nullable=True)
