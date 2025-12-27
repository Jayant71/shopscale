from fastapi import FastAPI, Depends, HTTPException
from .routers import products
from dotenv import load_dotenv
from .database import engine, Base

load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(
    products.router
)


@app.get("/")
def root():
    return {"Hello": "World"}
