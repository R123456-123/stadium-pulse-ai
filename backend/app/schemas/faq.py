"""FAQ response schemas."""

from pydantic import BaseModel


class FAQResponse(BaseModel):
    """FAQ entry data returned by the API."""

    id: int
    question: str
    question_hi: str
    answer: str
    answer_hi: str
    category: str
    tags: str | None = None

    model_config = {"from_attributes": True}
