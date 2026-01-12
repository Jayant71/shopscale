from pyexpat import model
from turtle import st
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.oauth2 import get_current_user, is_admin
from .. import schemas, models

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[schemas.Product], status_code=status.HTTP_200_OK)
def read_products(db: Session = Depends(get_db), page: int = 1, limit: int = 1):
    skip = (page - 1) * limit
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=schemas.Product, status_code=status.HTTP_200_OK)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found with id {product_id}"
        )
    return db_product


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Product, dependencies=[Depends(is_admin)])
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), ):
    if product.price < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Price must be non-negative"
        )
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", status_code=status.HTTP_200_OK, response_model=schemas.Product, dependencies=[Depends(is_admin)])
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    if product.price is not None and product.price < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Price must be non-negative"
        )
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id).first()
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found with id {product_id}"
        )
    db.delete(product)
    db.commit()
    return
