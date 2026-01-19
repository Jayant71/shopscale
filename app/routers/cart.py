from fastapi import Depends, HTTPException, APIRouter, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import models, schemas
from app.database import get_db
from app.utils.oauth2 import get_current_user
from sqlalchemy.orm import joinedload, selectinload

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.CartItemInList])
async def get_cart_items(db: AsyncSession = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    result = await db.execute(select(models.Cart).filter(models.Cart.user_id == current_user.id))
    cart = result.scalars().first()
    if not cart:
        return []
    items = (
        await db.execute(
            select(models.CartItem)
            .options(joinedload(models.CartItem.product))
            .filter(models.CartItem.cart_id == cart.id)
        )
    )
    items = items.scalars().all()
    return items


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=schemas.CartItemInList)
async def add_item_to_cart(product_add: schemas.CartItemAdd, quantity: int = 1, db: AsyncSession = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    product = await db.get(models.Product, product_add.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_add.product_id} not found"
        )
    if product.stock_quantity < quantity:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with id {product_add.product_id} is out of stock"
        )

    result = await db.execute(
        select(models.Cart)
        .options(selectinload(models.Cart.cart_items).selectinload(models.CartItem.product))
        .filter(models.Cart.user_id == current_user.id)
    )
    cart = result.scalars().first()
    if not cart:
        cart = models.Cart(user_id=current_user.id)
        db.add(cart)
        await db.flush()
        cart.cart_items = []

    cart_item = next(
        (item for item in cart.cart_items if item.product_id == product.id),
        None,
    )
    if cart_item:
        cart_item.quantity += quantity  # type: ignore
    else:
        cart_item = models.CartItem(
            cart_id=cart.id,
            product_id=product.id,  # type: ignore[arg-type]
            quantity=quantity,
        )
        db.add(cart_item)
        cart.cart_items.append(cart_item)

    product.stock_quantity -= quantity  # type: ignore
    await db.flush()
    await db.refresh(cart_item, attribute_names=["product"])

    # Build response before commit to avoid detached instance issues
    response_payload = schemas.CartItemInList(
        id=cart_item.id,  # type: ignore
        product=schemas.ProductInCart(
            id=cart_item.product.id,
            name=cart_item.product.name,
            description=cart_item.product.description,
            price=cart_item.product.price,
            category_id=cart_item.product.category_id,
        ),
        quantity=cart_item.quantity,  # type: ignore
    )
    await db.commit()

    return response_payload


@router.delete("/{product_remove}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(product_remove: int, quantity: int = 1, db: AsyncSession = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    result = await db.execute(select(models.Cart).filter(models.Cart.user_id == current_user.id))
    cart = result.scalars().first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    result = await db.execute(select(models.CartItem).filter(models.CartItem.cart_id ==
                                                             cart.id, models.CartItem.product_id == product_remove))
    cart_item = result.scalars().first()
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
    result = await db.execute(select(models.Product).filter(models.Product.id == product_remove))
    product = result.scalars().first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not in inventory"
        )
    cart_item.quantity -= quantity  # type: ignore
    product.stock_quantity += quantity  # type: ignore
    if cart_item.quantity == 0:  # type: ignore
        await db.delete(cart_item)
    await db.commit()
    return


@router.post("/checkout", status_code=status.HTTP_200_OK, response_model=schemas.Order)
async def checkout_cart(db: AsyncSession = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    result = await db.execute(select(models.Cart).filter(
        models.Cart.user_id == current_user.id))
    cart = result.scalars().first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    result = await db.execute(
        select(models.CartItem)
        .options(joinedload(models.CartItem.product))
        .filter(models.CartItem.cart_id == cart.id)
    )
    items = result.scalars().all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    total_amount = 0.0
    order = models.Order(user_id=current_user.id, total_amount=0.0)
    db.add(order)
    await db.flush()
    await db.refresh(order)
    for item in items:
        product: models.Product = item.product
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=product.id,  # type: ignore
            quantity=item.quantity,
            price_at_purchase=product.price  # type: ignore
        )
        db.add(order_item)
        total_amount += product.price * item.quantity  # type: ignore
        await db.delete(item)
    order.total_amount = total_amount  # type: ignore
    order_id = order.id
    await db.commit()
    result = await db.execute(
        select(models.Order)
        .options(selectinload(models.Order.order_items))
        .filter(models.Order.id == order_id)
    )
    order_with_items = result.scalars().unique().one()
    return order_with_items
