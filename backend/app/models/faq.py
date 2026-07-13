"""FAQ model representing the stadium knowledge base.

Stores bilingual question-answer pairs categorized by topic.
This is the retrieval layer that Gemini's function calling searches
when fans ask questions — it grounds responses in verified information
instead of generating answers from parametric knowledge.

Design decision:
    Tags are stored as a comma-separated string rather than a separate
    tags table. For a knowledge base of <100 entries and simple keyword
    search, a JOIN-free approach keeps the function-calling hot path fast.
    A full-text search index would be the next step if the KB grows.
"""

from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FAQEntry(Base):
    """A bilingual knowledge base entry with category and search tags."""

    __tablename__ = "faq_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text)
    question_hi: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    answer_hi: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(30))
    # "general" | "accessibility" | "safety" | "food" | "transport" | "rules"
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Comma-separated keywords for simple search, e.g. "wheelchair,ramp,accessible"
