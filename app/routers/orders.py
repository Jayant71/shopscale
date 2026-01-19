from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas
from app.database import get_db
from app.utils.oauth2 import get_current_user
from sqlalchemy.orm import joinedload


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.Order])
async def read_orders(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        result = await db.execute(
            select(models.Order)
            .options(joinedload(models.Order.order_items))
            .where(models.Order.user_id == current_user.id)
            .order_by(models.Order.created_at.desc())
        )
        orders = result.unique().scalars().all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching orders: {}".format(str(e))
        )
    return orders
