"""CRUD operations for the User model."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session,
    db_user: models.User,
    user: schemas.BaseModel,
    partial: bool = True,
) -> models.User:
    # PATCH (partial=True): only apply fields present in the request.
    # PUT  (partial=False): apply all fields, resetting omitted optionals
    # to their schema defaults for true full-replacement semantics.
    update_data = user.model_dump(exclude_unset=partial)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: models.User) -> None:
    db.delete(db_user)
    db.commit()
