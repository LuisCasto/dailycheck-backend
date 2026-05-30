from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.habit import Habit
from app.models.habit_log import HabitLog
from app.models.user import User
from app.schemas.habit_log import HabitLogCreate, HabitLogOut, HabitLogUpdate, StatsOut

router = APIRouter(prefix="/api/logs", tags=["logs"])


def get_owned_habit_or_404(habit_id: UUID, current_user: User, db: Session) -> Habit:
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id,
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habito no encontrado")
    return habit


def get_owned_log_or_404(log_id: UUID, current_user: User, db: Session) -> HabitLog:
    log = db.query(HabitLog).filter(
        HabitLog.id == log_id,
        HabitLog.user_id == current_user.id,
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")
    return log


@router.get("", response_model=List[HabitLogOut])
def get_logs(
    log_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(HabitLog).filter(HabitLog.user_id == current_user.id)
    if log_date:
        query = query.filter(HabitLog.date == log_date)
    return query.all()


def toggle_habit_log(
    data: HabitLogCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_habit_or_404(data.habit_id, current_user, db)

    existing = db.query(HabitLog).filter(
        HabitLog.habit_id == data.habit_id,
        HabitLog.user_id == current_user.id,
        HabitLog.date == data.date,
    ).first()
    if existing:
        deleted_log_id = existing.id
        db.delete(existing)
        db.commit()
        response.status_code = status.HTTP_200_OK
        return {
            "detail": "Log eliminado",
            "deleted": True,
            "log_id": deleted_log_id,
            "habit_id": data.habit_id,
            "date": data.date,
        }

    log = HabitLog(
        habit_id=data.habit_id,
        user_id=current_user.id,
        date=data.date,
        completed=True,
        note=data.note,
    )
    db.add(log)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Ya existe un log para este habito en esa fecha",
        )

    db.refresh(log)
    response.status_code = status.HTTP_201_CREATED
    return log


@router.post("")
def create_log(
    data: HabitLogCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return toggle_habit_log(data, response, db, current_user)


@router.post("/toggle")
def toggle_log(
    data: HabitLogCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return toggle_habit_log(data, response, db, current_user)


@router.get("/stats/{habit_id}", response_model=StatsOut)
def get_stats(
    habit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_habit_or_404(habit_id, current_user, db)

    total = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.completed == True,
    ).count()

    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    completed_30d = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date >= thirty_days_ago,
        HabitLog.completed == True,
    ).count()
    rate = round((completed_30d / 30) * 100)

    streak = 0
    for i in range(365):
        check_date = today - timedelta(days=i)
        exists = db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id,
            HabitLog.date == check_date,
            HabitLog.completed == True,
        ).first()
        if exists:
            streak += 1
        elif i > 0:
            break

    return StatsOut(
        habit_id=habit_id,
        streak=streak,
        completion_rate_30d=rate,
        total_logs=total,
    )


@router.get("/{log_id}", response_model=HabitLogOut)
def get_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_log_or_404(log_id, current_user, db)


@router.patch("/{log_id}", response_model=HabitLogOut)
def update_log(
    log_id: UUID,
    data: HabitLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = get_owned_log_or_404(log_id, current_user, db)
    payload = data.model_dump(exclude_unset=True)

    if "date" in payload:
        log.date = payload["date"]
    if "completed" in payload:
        log.completed = payload["completed"]
    if "note" in payload:
        log.note = payload["note"]

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Ya existe un log para este habito en esa fecha",
        )

    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=204)
def delete_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = get_owned_log_or_404(log_id, current_user, db)
    db.delete(log)
    db.commit()
