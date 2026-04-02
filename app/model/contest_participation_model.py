from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, CheckConstraint, func, ForeignKey, UniqueConstraint

from app.core.database import Base
from datetime import datetime

class ContestParticipation(Base):
    __tablename__="contest_participations"
    __table_args__=(
        UniqueConstraint("user_id", "contest_id", name="uq_contest_participations_user_contest"),
        CheckConstraint("evaluation_count >= 0", name="ck_contest_participations_evaluation_nonnegative")
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    has_submitted_entry: Mapped[bool] = mapped_column(default=False, nullable=False)
    evaluation_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    contest: Mapped["Contest"] = relationship(
        "Contest",
        back_populates="contest_participations"
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="contest_participations"
    )
    