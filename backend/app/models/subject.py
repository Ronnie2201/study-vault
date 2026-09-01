from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .deadline import Deadline
    from .note import Note
    from .user import User


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # e.g., "SMA 210"
    color: Mapped[str] = mapped_column(
        String(7), default="#3B82F6"
    )  # Hex color for UI
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    user: Mapped[User] = relationship(back_populates="subjects")
    notes: Mapped[list[Note]] = relationship(
        back_populates="subject", cascade="all, delete-orphan"
    )
    deadlines: Mapped[list[Deadline]] = relationship(
        back_populates="subject", cascade="all, delete-orphan"
    )
