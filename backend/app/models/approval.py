from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.letter import Letter


class Approval(Base):
    __tablename__ = "approvals"

    letter_id: Mapped[int] = mapped_column(Integer, ForeignKey("letters.id"), nullable=False)
    draft_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("drafts.id"), nullable=True)
    route: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    current_approver: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approval_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    operation_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    request_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    geography: Mapped[str | None] = mapped_column(String(100), nullable=True)
    client_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    document_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    change_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    letter: Mapped["Letter"] = relationship("Letter", back_populates="approvals")

