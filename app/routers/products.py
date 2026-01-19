from turtle import st
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from app.database import get_db
from app.utils.oauth2 import get_current_user, is_admin
from .. import schemas, models
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[schemas.Product], status_code=status.HTTP_200_OK)
async def read_products(db: AsyncSession = Depends(get_db), page: int = 1, limit: int = 10):
    skip = (page - 1) * limit
    products = await db.execute(
        select(models.Product).offset(skip).limit(limit))
    return products.scalars().all()


@router.get("/{product_id}", response_model=schemas.Product, status_code=status.HTTP_200_OK)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Product).filter(
        models.Product.id == product_id))
    db_product = result.scalars().first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found with id {product_id}"
        )
    return db_product


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Product, dependencies=[Depends(is_admin)])
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(get_db), ):
    if product.price < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Price must be non-negative"
        )
    if product.stock_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Stock quantity must be non-negative"
        )
    id = await db.execute(select(models.Category).filter(
        models.Category.id == product.category_id))
    id = id.scalars().first()
    if not id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category not found with id {product.category_id}"
        )
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.put("/{product_id}", status_code=status.HTTP_200_OK, response_model=schemas.Product, dependencies=[Depends(is_admin)])
async def update_product(product_id: int, product: schemas.ProductUpdate, db: AsyncSession = Depends(get_db)):
    if product.price is not None and product.price < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Price must be non-negative"
        )
    db_product = await db.execute(select(models.Product).filter(
        models.Product.id == product_id))
    db_product = db_product.scalars().first()
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(is_admin)])
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await db.execute(select(models.Product).filter(
        models.Product.id == product_id))
    product = product.scalars().first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found with id {product_id}"
        )
    await db.delete(product)
    await db.commit()
    return
