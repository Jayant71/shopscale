from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from app.database import get_db
from .. import schemas, models
from app.utils.oauth2 import get_password_hash, is_admin, verify_password, get_current_user, create_access_token, get_token_data
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def register_user(user_create: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(models.User).filter(
        models.User.email == user_create.email))
    existing_user = existing_user.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user_create.password)

    new_user = models.User(
        full_name=user_create.fullname,
        email=user_create.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.flush()
    cart = models.Cart(user_id=new_user.id)
    db.add(cart)

    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.get("/users", response_model=List[schemas.User], dependencies=[Depends(is_admin)])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.role == "client"))
    user = result.scalars().all()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found"
        )
    return user


@router.post("/login", response_model=schemas.Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(
        models.User.email == form_data.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not registered"
        )
    if not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong password"
        )
    access_token = create_access_token(
        data={"id": user.id, "role": user.role, "username": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


# Test route to verify the token data
@router.post("/verifytoken", response_model=schemas.TokenData)
def verify_token(token: schemas.TokenRequest):
    return get_token_data(token=token.token)
