"""Models package — imports all ORM models so SQLAlchemy metadata is complete.

This file serves a critical purpose: by importing every model here,
we ensure that Base.metadata knows about all tables when create_tables()
is called. Without these imports, SQLAlchemy would silently skip
creating tables for models that haven't been imported yet.

Usage:
    from app.models import Zone, Gate, Facility  # noqa: F401
"""

from app.models.crowd_snapshot import CrowdSnapshot
from app.models.facility import Facility
from app.models.faq import FAQEntry
from app.models.gate import Gate
from app.models.transport import TransportOption
from app.models.zone import Zone

__all__ = [
    "CrowdSnapshot",
    "Facility",
    "FAQEntry",
    "Gate",
    "TransportOption",
    "Zone",
]
