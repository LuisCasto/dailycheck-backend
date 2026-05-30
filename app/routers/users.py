from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.security import hash_password
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])


def get_owned_user_or_404(user_id: UUID, current_user: User, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este usuario")
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_owned_user_or_404(user_id, current_user, db)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_owned_user_or_404(user_id, current_user, db)
    payload = data.model_dump(exclude_unset=True)

    new_email = payload.get("email")
    if new_email and new_email != user.email:
        existing = db.query(User).filter(User.email == new_email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email ya registrado")

    if "name" in payload:
        user.name = payload["name"]
    if "email" in payload:
        user.email = payload["email"]
    if "password" in payload and payload["password"]:
        user.hashed_password = hash_password(payload["password"])

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_owned_user_or_404(user_id, current_user, db)
    db.delete(user)
    db.commit()
