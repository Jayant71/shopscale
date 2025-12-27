from fastapi import FastAPI, Depends, HTTPException
from .routers import products
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(
    products.router
)


@app.get("/")
def root():
    return {"Hello": "World"}
