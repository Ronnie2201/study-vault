from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

class DeadlineType(str, Enum):
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    OTHER = "other"

class Deadline(Base):
    __tablename__ = "deadlines"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        index=True  # We'll query deadlines by date frequently
    )
    type: Mapped[DeadlineType] = mapped_column(
        SQLAlchemyEnum(DeadlineType),
        default=DeadlineType.OTHER,
        nullable=False
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean, 
        default=False,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    subject: Mapped["Subject"] = relationship(back_populates="deadlines")
