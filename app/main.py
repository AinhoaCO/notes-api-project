import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, engine, SessionLocal
from app import models
from app.routes import router as notes_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title="Notes API",
    description="Python implementation of the seminar Notes API",
    version="1.0.0",
    lifespan=lifespan
)


# CORS configuration
cors_origin = os.getenv(
    "CORS_ORIGIN",
    "http://localhost:3000"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)


# Register notes routes
app.include_router(notes_router)


# GET /api/message
@app.get("/api/message")
def get_message():

    return {
        "message": os.getenv(
            "APP_MESSAGE",
            "Hello from the Notes API"
        ),
        "version": os.getenv(
            "APP_VERSION",
            "dev"
        )
    }


# GET /livez
@app.get("/livez")
def liveness():

    return {
        "status": "alive"
    }


# GET /readyz
@app.get("/readyz")
def readiness():

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))

        return {
            "status": "ready"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )