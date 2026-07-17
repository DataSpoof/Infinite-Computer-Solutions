"""Application entry point."""

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import users

# Create database tables on startup (fine for demos; use migrations in prod).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI CRUD",
    description="A simple CRUD API for managing users.",
    version="1.0.0",
)

app.include_router(users.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI CRUD API"}
