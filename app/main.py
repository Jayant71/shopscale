from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.core.middleware import add_process_time_header
from app.routers import cart, category, orders
from .routers import products, auth
from .database import engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(auth.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(category.router)


@app.middleware("http")
async def process_time_middleware(request, call_next):
    return await add_process_time_header(request, call_next)


@app.get("/")
def root():
    return {"message": "Welcome to ShopScale API"}
