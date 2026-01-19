from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.database import get_db
from app.utils.oauth2 import is_admin

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=list[schemas.Category])
async def read_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category))
    categories = result.scalars().all()
    return categories


@router.get("/{category_id}", response_model=schemas.Category)
async def read_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category).filter(models.Category.id == category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/add", response_model=schemas.Category, status_code=201, dependencies=[Depends(is_admin)])
async def create_category(category: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=schemas.Category, dependencies=[Depends(is_admin)])
async def update_category(category_id: int, category: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Category).filter(models.Category.id == category_id))
    db_category = result.scalars().first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.model_dump().items():
        setattr(db_category, key, value)
    await db.commit()
    await db.refresh(db_category)
    return db_category
