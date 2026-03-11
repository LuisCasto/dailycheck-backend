from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.models.habit import Habit
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitUpdate, HabitOut
from app.core.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/habits", tags=["habits"])

@router.get("", response_model=List[HabitOut])
def get_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Habit).filter(Habit.user_id == current_user.id).all()

@router.post("", response_model=HabitOut, status_code=201)
def create_habit(
    data: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = Habit(**data.model_dump(), user_id=current_user.id)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

@router.put("/{habit_id}", response_model=HabitOut)
def update_habit(
    habit_id: UUID,
    data: HabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)
    return habit

@router.delete("/{habit_id}", status_code=204)
def delete_habit(
    habit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    db.delete(habit)
    db.commit()