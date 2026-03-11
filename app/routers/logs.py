from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import date, timedelta
from app.database import get_db
from app.models.habit_log import HabitLog
from app.models.habit import Habit
from app.models.user import User
from app.schemas.habit_log import HabitLogCreate, HabitLogOut, StatsOut
from app.core.auth import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("", response_model=List[HabitLogOut])
def get_logs(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(HabitLog).filter(HabitLog.user_id == current_user.id)
    if log_date:
        query = query.filter(HabitLog.date == log_date)
    return query.all()

@router.post("", response_model=HabitLogOut, status_code=201)
def toggle_log(
    data: HabitLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verificar que el hábito pertenece al usuario
    habit = db.query(Habit).filter(
        Habit.id == data.habit_id,
        Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Hábito no encontrado")

    # Si ya existe el log, lo elimina (toggle)
    existing = db.query(HabitLog).filter(
        HabitLog.habit_id == data.habit_id,
        HabitLog.date == data.date
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        raise HTTPException(status_code=200, detail="Log eliminado")

    log = HabitLog(
        habit_id=data.habit_id,
        user_id=current_user.id,
        date=data.date,
        completed=True,
        note=data.note,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.get("/stats/{habit_id}", response_model=StatsOut)
def get_stats(
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

    total = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.completed == True
    ).count()

    # Completion rate últimos 30 días
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    completed_30d = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date >= thirty_days_ago,
        HabitLog.completed == True
    ).count()
    rate = round((completed_30d / 30) * 100)

    # Racha actual
    streak = 0
    for i in range(365):
        check_date = today - timedelta(days=i)
        exists = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == check_date,
            HabitLog.completed == True
        ).first()
        if exists:
            streak += 1
        elif i > 0:
            break

@router.patch("/{log_id}/note", response_model=HabitLogOut)
def update_note(
    log_id: UUID,
    note: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = db.query(HabitLog).filter(
        HabitLog.id == log_id,
        HabitLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")
    log.note = note
    db.commit()
    db.refresh(log)
    return log

    return StatsOut(habit_id=habit_id, streak=streak, completion_rate_30d=rate, total_logs=total)