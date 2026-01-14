from datetime import datetime
from typing import List, Optional
from venv import create
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    fullname: Optional[str] = None
    password: str


class UserLogin(UserBase):
    password: str


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool

    class ConfigDict:
        from_attributes = True


class User(UserBase):
    id: int
    is_active: bool
    role: str

    class ConfigDict:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None
    username: str | None = None
    role: str


class TokenRequest(BaseModel):
    token: str


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock_quantity: int = 0
    category_id: int


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock_quantity: int | None = None
    category_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    id: int
    user_id: int

    class ConfigDict:
        from_attributes = True


class CartItem(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    class ConfigDict:
        from_attributes = True


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartitemRemove(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemInList(BaseModel):
    id: int
    product: Product
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    user_id: int
    total_amount: float

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(OrderBase):
    pass


class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    model_config = ConfigDict(from_attributes=True)


class OrderItem(OrderItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Order(OrderBase):
    id: int
    order_items: List[OrderItem] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class Category(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
