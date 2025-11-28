from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.draft import Draft
    from app.models.approval import Approval


class Letter(Base):
    __tablename__ = "letters"

    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    sender_email: Mapped[str] = mapped_column(String(255), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    request_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    processing_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    client_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correspondence_thread_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    drafts: Mapped[list["Draft"]] = relationship("Draft", back_populates="letter", cascade="all, delete-orphan")
    approvals: Mapped[list["Approval"]] = relationship("Approval", back_populates="letter", cascade="all, delete-orphan")

