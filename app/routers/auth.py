from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from .. import schemas, models
from app.utils.oauth2 import get_password_hash, verify_password, get_current_user, create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def register_user(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_create.password)

    new_user = models.User(
        email=user_create.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/users", response_model=List[schemas.User])
def get_all_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    user = db.query(models.User).all()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    return user


@router.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    if not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong password"
        )
    access_token = create_access_token(data={"id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
