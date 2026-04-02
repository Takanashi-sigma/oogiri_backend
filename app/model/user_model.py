from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    comparisons: Mapped[list["Comparison"]] = relationship(
        "Comparison",
        foreign_keys="Comparison.voter_user_id",
        back_populates="voter_user"
    )
    entries: Mapped[list["Entry"]] = relationship(
        "Entry",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    contest_participations: Mapped[list["ContestParticipation"]] = relationship(
        "ContestParticipation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
