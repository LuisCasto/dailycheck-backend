from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal

FrequencyType = Literal["daily", "weekly", "monthly"]

class HabitCreate(BaseModel):
    name: str
    description: str = ""
    category: str = "Otro"
    icon: str = "🎯"
    daily_task: str
    target_value: Optional[int] = None
    unit: Optional[str] = None
    frequency: FrequencyType = "daily"
    times_per_period: int = 1

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    daily_task: Optional[str] = None
    target_value: Optional[int] = None
    unit: Optional[str] = None
    frequency: Optional[FrequencyType] = None
    times_per_period: Optional[int] = None

class HabitOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str
    category: str
    icon: str
    daily_task: str
    target_value: Optional[int]
    unit: Optional[str]
    frequency: str
    times_per_period: int
    created_at: datetime

    model_config = {"from_attributes": True}