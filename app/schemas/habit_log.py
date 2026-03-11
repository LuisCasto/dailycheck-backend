from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class HabitLogCreate(BaseModel):
    habit_id: UUID
    date: date
    note: Optional[str] = None

class HabitLogOut(BaseModel):
    id: UUID
    habit_id: UUID
    user_id: UUID
    date: date
    completed: bool
    note: Optional[str]
    logged_at: datetime

    model_config = {"from_attributes": True}

class StatsOut(BaseModel):
    habit_id: UUID
    streak: int
    completion_rate_30d: int
    total_logs: int