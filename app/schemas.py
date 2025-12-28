from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
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

    class ConfigDict:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None
    username: str | None = None


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


class ProductUpdate(BaseModel):
    id: int | None = None
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock_quantity: int | None = None
    category_id: int | None = None

    class ConfigDict:
        from_attributes = True
