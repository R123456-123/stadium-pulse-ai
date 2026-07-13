"""Zone response schemas.

Two schema variants:
    - ZoneSummary: lightweight, used in list endpoints and WebSocket pushes.
      Includes computed density_pct for quick visual representation.
    - ZoneDetail: full zone data with nested gates and facilities.
      Used when viewing a specific zone.
"""

from pydantic import BaseModel, computed_field

from app.schemas.facility import FacilityResponse
from app.schemas.gate import GateResponse


class ZoneSummary(BaseModel):
    """Lightweight zone data for list views and real-time updates.

    density_pct is computed rather than stored because current_occupancy
    changes every simulator tick — computing it on-the-fly avoids
    stale percentage values.
    """

    id: str
    name: str
    name_hi: str
    capacity: int
    current_occupancy: int
    zone_type: str
    description: str | None = None
    description_hi: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def density_pct(self) -> float:
        """Current occupancy as a percentage of capacity."""
        if self.capacity <= 0:
            return 0.0
        return round((self.current_occupancy / self.capacity) * 100, 1)

    model_config = {"from_attributes": True}


class ZoneDetail(ZoneSummary):
    """Full zone data including nested gates and facilities.

    Extends ZoneSummary with relationship data. Used for single-zone
    detail views where the frontend needs everything in one call.
    """

    gates: list[GateResponse] = []
    facilities: list[FacilityResponse] = []
