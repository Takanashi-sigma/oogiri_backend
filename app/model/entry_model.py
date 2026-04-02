from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, CheckConstraint, func, ForeignKey, UniqueConstraint, Text, Float
from app.core.database import Base
from datetime import datetime

class Entry(Base):
    __tablename__="entries"
    __table_args__=(
        UniqueConstraint("user_id", "contest_id", name="uq_entries_contest_user"),
        CheckConstraint("rd >= 0", name="ck_entries_rd_nonnegative"),
        CheckConstraint("volatility >= 0", name="ck_entries_volatility_nonnegative"),
        CheckConstraint("comparisons_count >= 0", name="ck_entries_comparisons_count_nonnegative"),
        CheckConstraint("wins >= 0",  name="ck_entries_wins_nonnegative"),
        CheckConstraint("losses >= 0", name="ck_entries_losses_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=1500.0)
    rd: Mapped[float] = mapped_column(Float, nullable=False, default=350.0)
    volatility: Mapped[float] = mapped_column(Float, nullable=False, default=0.06)
    comparisons_count: Mapped[int] = mapped_column(nullable=False, default=0)
    wins: Mapped[int] = mapped_column(nullable=False, default=0)
    losses: Mapped[int] = mapped_column(nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    contest: Mapped["Contest"] = relationship(
        "Contest",
        back_populates="entries"
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="entries"
    )
    comparisons_as_a: Mapped[list["Comparison"]] = relationship(
        "Comparison",
        foreign_keys="Comparison.entry_a_id",
        back_populates="entry_a"
    )
    comparisons_as_b: Mapped[list["Comparison"]] = relationship(
        "Comparison",
        foreign_keys="Comparison.entry_b_id",
        back_populates="entry_b"
    )
    comparisons_as_chosen: Mapped[list["Comparison"]] = relationship(
        "Comparison",
        foreign_keys="Comparison.chosen_entry_id",
        back_populates="chosen_entry"
    )
