from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    await create_tables()
    print("Database tables created successfully!")
    yield


app = FastAPI(
    title="GetNews API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", description="Health check", tags=["Health check"])
async def health_check():
    return {"status": "healthy"}