import uuid
from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, default=True)
    note = Column(String, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    habit = relationship("Habit", back_populates="logs")

    __table_args__ = (
        UniqueConstraint("habit_id", "date", name="uq_habit_log_per_day"),
    )