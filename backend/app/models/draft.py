from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.letter import Letter


class DraftStatus(str, enum.Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    APPROVED = "approved"
    SENT = "sent"
    REJECTED = "rejected"


class Draft(Base):
    __tablename__ = "drafts"

    letter_id: Mapped[int] = mapped_column(Integer, ForeignKey("letters.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    validation_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validation_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[DraftStatus] = mapped_column(Enum(DraftStatus), nullable=False, default=DraftStatus.DRAFT)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    letter: Mapped["Letter"] = relationship("Letter", back_populates="drafts")

