from pydantic import BaseModel


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

    class ConfigDict:
        from_attributes = True
