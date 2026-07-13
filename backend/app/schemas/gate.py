"""Gate response schemas."""

from pydantic import BaseModel, computed_field


class GateResponse(BaseModel):
    """Gate data returned by the API.

    Includes a computed estimated_wait_minutes derived from
    current_queue_length and capacity_per_minute — this is
    the number fans actually care about, not raw queue counts.
    """

    id: str
    name: str
    name_hi: str
    zone_id: str
    gate_type: str
    is_accessible: bool
    capacity_per_minute: int
    current_queue_length: int
    status: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def estimated_wait_minutes(self) -> float:
        """Estimate wait time based on queue length and throughput.

        Simple model: wait = queue_length / capacity_per_minute.
        Returns 0.0 for gates with no queue.
        """
        if self.capacity_per_minute <= 0 or self.current_queue_length <= 0:
            return 0.0
        return round(self.current_queue_length / self.capacity_per_minute, 1)

    model_config = {"from_attributes": True}
