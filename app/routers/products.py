from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from .. import schemas, models

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/")
def read_products():
    return {"message": "List of products"}


@router.get("/{product_id}")
def read_product(product_id: int):
    return {"message": f"Details of product {product_id}"}


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    if product.price < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Price must be non-negative"
        )
    db.add(models.Product(**product.model_dump()))
    db.commit()
    created_product = schemas.Product(**product.model_dump(), id=1)
    return created_product


@router.put("/{product_id}")
def update_product(product_id: int):
    return {"message": f"Product {product_id} updated"}


@router.delete("/{product_id}")
def delete_product(product_id: int):
    return {"message": f"Product {product_id} deleted"}
