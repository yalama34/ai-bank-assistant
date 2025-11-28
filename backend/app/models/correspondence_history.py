from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from ..models.base import Base


class CorrespondenceDirection(str, enum.Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class CorrespondenceHistory(Base):
    __tablename__ = "correspondence_history"

    correspondence_thread_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    client_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    letter_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("letters.id"), nullable=True)
    direction: Mapped[CorrespondenceDirection] = mapped_column(Enum(CorrespondenceDirection), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    sender: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recipient: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

