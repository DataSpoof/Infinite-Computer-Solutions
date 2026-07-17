"""User API routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, email=user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.get("/", response_model=List[schemas.UserOut])
def read_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=schemas.UserOut)
def replace_user(
    user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)
):
    """Full replacement: every field must be supplied (REST `PUT` semantics)."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Guard against replacing with an email owned by a different user.
    existing = crud.get_user_by_email(db, email=user.email)
    if existing and existing.id != user_id:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.update_user(db=db, db_user=db_user, user=user, partial=False)


@router.patch("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)
):
    """Partial update: only the supplied fields are changed (`PATCH` semantics)."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Guard against updating to an email owned by a different user.
    if user.email:
        existing = crud.get_user_by_email(db, email=user.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already registered")

    return crud.update_user(db=db, db_user=db_user, user=user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db=db, db_user=db_user)
    return None
