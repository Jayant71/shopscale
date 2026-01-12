from fastapi import FastAPI, Depends, HTTPException

from app.routers import cart
from .routers import products, auth
from dotenv import load_dotenv
from .database import engine, Base

load_dotenv()
Base.metadata.create_all(bind=engine)
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

@app.get("/")
def root():
    return {"message": "Welcome to ShopScale API"}
