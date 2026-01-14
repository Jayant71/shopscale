from urllib import response
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from websockets import route

from app import models, schemas
from app.database import get_db
from app.utils.oauth2 import is_admin

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=list[schemas.Category])
def read_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories


@router.get("/{category_id}", response_model=schemas.Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(
        models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=schemas.Category, status_code=201, dependencies=[Depends(is_admin)])
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=schemas.Category, dependencies=[Depends(is_admin)])
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.model_dump().items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category
