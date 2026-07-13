"""Transport option response schemas."""

from pydantic import BaseModel


class TransportResponse(BaseModel):
    """Transport option data returned by the API."""

    id: int
    name: str
    name_hi: str
    transport_type: str
    nearest_gate_id: str | None = None
    estimated_walk_minutes: int
    accessibility_notes: str | None = None
    accessibility_notes_hi: str | None = None
    schedule_info: str | None = None
    schedule_info_hi: str | None = None

    model_config = {"from_attributes": True}
