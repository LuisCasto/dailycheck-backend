from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.habit import Habit
from app.models.user import User
from app.schemas.habit import HabitCreate, HabitOut, HabitUpdate

router = APIRouter(prefix="/api/habits", tags=["habits"])


def get_owned_habit_or_404(habit_id: UUID, current_user: User, db: Session) -> Habit:
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id,
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habito no encontrado")
    return habit


@router.get("", response_model=List[HabitOut])
def get_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Habit).filter(Habit.user_id == current_user.id).all()


@router.get("/{habit_id}", response_model=HabitOut)
def get_habit(
    habit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_habit_or_404(habit_id, current_user, db)


@router.post("", response_model=HabitOut, status_code=201)
def create_habit(
    data: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(get_current_user),
):
    habit = get_owned_habit_or_404(habit_id, current_user, db)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=204)
def delete_habit(
    habit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    habit = get_owned_habit_or_404(habit_id, current_user, db)
    db.delete(habit)
    db.commit()
