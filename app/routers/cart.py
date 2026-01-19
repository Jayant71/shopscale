from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.utils.oauth2 import get_current_user
from sqlalchemy.orm import joinedload

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.CartItemInList])
def get_cart_items(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id).first()
    if not cart:
        return []
    items = (
        db.query(models.CartItem)
        .options(joinedload(models.CartItem.product))
        .filter(models.CartItem.cart_id == cart.id)
        .all()
    )
    return items


@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_item_to_cart(product_add: schemas.CartItemAdd, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    product = db.query(models.Product).filter(
        models.Product.id == product_add.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_add.product_id} not found"
        )
    if product.stock_quantity < 1:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with id {product_add.product_id} is out of stock"
        )
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id).first()
    if not cart:
        cart = models.Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id, models.CartItem.product_id == product.id).first()
    if cart_item:
        cart_item.quantity += 1  # type: ignore
    else:
        cart_item = models.CartItem(
            cart_id=cart.id, product_id=product.id, quantity=1)
        db.add(cart_item)
    product.stock_quantity -= 1  # type: ignore
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_cart(product_remove: int, quantity: int = 1, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    cart_item = db.query(models.CartItem).filter(models.CartItem.cart_id ==
                                                 cart.id, models.CartItem.product_id == product_remove).first()
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not in cart"
        )
    if cart_item.quantity < quantity:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot remove more items than present in cart"
        )
    product = db.query(models.Product).filter(
        models.Product.id == product_remove).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not in inventory"
        )
    cart_item.quantity -= quantity  # type: ignore
    product.stock_quantity += quantity  # type: ignore
    if cart_item.quantity == 0:  # type: ignore
        db.delete(cart_item)
    db.commit()
    return


@router.post("/checkout", status_code=status.HTTP_200_OK, response_model=schemas.Order)
def checkout_cart(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    items = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    total_amount = 0.0
    order = models.Order(user_id=current_user.id, total_amount=0.0)
    db.add(order)
    db.commit()
    db.refresh(order)
    for item in items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id).first()
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=product.id,  # type: ignore
            quantity=item.quantity,
            price_at_purchase=product.price  # type: ignore
        )
        db.add(order_item)
        total_amount += product.price * item.quantity  # type: ignore
        db.delete(item)
    order.total_amount = total_amount  # type: ignore
    db.commit()
    db.refresh(order)
    return order
