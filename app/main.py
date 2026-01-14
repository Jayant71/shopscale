from fastapi import FastAPI, Depends, HTTPException
from app import models
from app.core.middleware import add_process_time_header
from app.routers import cart, category, orders
from .routers import products, auth
from dotenv import load_dotenv
from .database import engine

load_dotenv()
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(
    products.router
)
app.include_router(
    auth.router
)
app.include_router(
    cart.router
)
app.include_router(
    orders.router
)

app.include_router(
    category.router
)


@app.middleware("http")
async def process_time_middleware(request, call_next):
    return await add_process_time_header(request, call_next)


@app.get("/")
def root():
    return {"message": "Welcome to ShopScale API"}
