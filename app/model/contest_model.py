from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Enum, CheckConstraint, func, Date, String
import enum
from app.core.database import Base
from datetime import datetime, date

class ContestStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    closed = "closed"

class Contest(Base):
    __tablename__ = "contests"
    __table_args__=(
        CheckConstraint("start_at < end_at", name="ck_contest_start_before_end"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False, index=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(225), nullable=True)
    prompt: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[ContestStatus] = mapped_column(
        Enum(ContestStatus, name="contest_status"),
        default=ContestStatus.draft,
        nullable=False,
        index=True
    )
    start_at: Mapped[date] = mapped_column(Date, nullable=False)
    end_at: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    entries: Mapped[list["Entry"]] = relationship(
        "Entry",
        back_populates="contest",
        cascade="all, delete-orphan"
    )
    contest_participations: Mapped[list["ContestParticipation"]] = relationship(
        "ContestParticipation",
        back_populates="contest",
        cascade="all, delete-orphan"
    )
    comparisons: Mapped[list["Comparison"]] = relationship(
        "Comparison",
        back_populates="contest",
        cascade="all, delete-orphan"
    )


