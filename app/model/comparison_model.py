from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, CheckConstraint, func, ForeignKey, Float

from app.core.database import Base
from datetime import datetime

class Comparison(Base):
    __tablename__="comparisons"
    __table_args__=(
        CheckConstraint("entry_a_id <> entry_b_id", name="ck_comparison_entry_a_not_entry_b"),
        CheckConstraint(
            "chosen_entry_id IN (entry_a_id, entry_b_id)",
            name="ck_comparison_chosen_entry_id"
        )
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id", ondelete="CASCADE"), nullable=False, index=True)
    voter_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_a_id: Mapped[int] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_b_id: Mapped[int] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False, index=True)
    chosen_entry_id: Mapped[int] = mapped_column(ForeignKey("entries.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_a_rating_before: Mapped[float] = mapped_column(Float, nullable=False)
    entry_b_rating_before: Mapped[float] = mapped_column(Float, nullable=False)
    entry_a_rd_before: Mapped[float] = mapped_column(Float, nullable=False)
    entry_b_rd_before: Mapped[float] = mapped_column(Float, nullable=False)
    entry_a_volatility_before: Mapped[float] = mapped_column(Float, nullable=False)
    entry_b_volatility_before: Mapped[float] = mapped_column(Float, nullable=False)
    entry_a_rating_after: Mapped[float] = mapped_column(Float, nullable=False)
    entry_b_rating_after: Mapped[float] = mapped_column(Float, nullable=False)
    entry_a_rd_after: Mapped[float] = mapped_column(Float, nullable=False)
    entry_b_rd_after: Mapped[float] = mapped_column(Float, nullable=False)
    entry_a_volatility_after: Mapped[float] = mapped_column(Float, nullable=False)
    entry_b_volatility_after: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    contest: Mapped["Contest"] = relationship(
        "Contest",
        back_populates="comparisons"
    )
    voter_user: Mapped["User"] = relationship(
        "User",
        back_populates="comparisons",
        foreign_keys=[voter_user_id]
    )
    entry_a: Mapped["Entry"] = relationship(
        "Entry",
        back_populates="comparisons_as_a",
        foreign_keys=[entry_a_id]
    )
    entry_b: Mapped["Entry"] = relationship(
        "Entry",
        back_populates="comparisons_as_b",
        foreign_keys=[entry_b_id]
    )
    chosen_entry: Mapped["Entry"] = relationship(
        "Entry",
        back_populates="comparisons_as_chosen",
        foreign_keys=[chosen_entry_id]
    )

