"""Facility response schemas."""

from pydantic import BaseModel


class FacilityResponse(BaseModel):
    """Facility data returned by the API."""

    id: int
    name: str
    name_hi: str
    zone_id: str
    facility_type: str
    is_accessible: bool
    floor_level: int
    description: str | None = None
    description_hi: str | None = None

    model_config = {"from_attributes": True}
