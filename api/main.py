"""Notes API: Python + FastAPI + Postgres.

Same contract as the seminar's Go API, so the reference React frontend works unchanged:
  GET  /api/message        -> {"message": ..., "version": ...}
  GET  /api/notes          -> [{"id", "text", "created_at"}], newest first
  POST /api/notes          -> body {"text": "..."}, returns the created note (201)
Extras (full CRUD, not used by the frontend):
  GET /api/notes/{id}, PUT /api/notes/{id}, DELETE /api/notes/{id}
Probes:
  GET /livez, GET /readyz

Configuration comes only from environment variables (12-factor):
  PORT, APP_MESSAGE, APP_VERSION, CORS_ORIGIN, DB_URL (required)
"""
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(level=logging.INFO, format='{"level":"%(levelname)s","msg":"%(message)s"}')
log = logging.getLogger("api")

APP_MESSAGE = os.getenv("APP_MESSAGE", "Hello from the API")
APP_VERSION = os.getenv("APP_VERSION", "dev")
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")
DB_URL = os.getenv("DB_URL")  # contains a password: never hardcode, never log

if not DB_URL:
    log.error("DB_URL is required")
    sys.exit(1)

pool = ConnectionPool(DB_URL, min_size=1, max_size=5, open=False, kwargs={"row_factory": dict_row})


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retry: in the cloud the DB can take a moment to accept connections.
    pool.open()
    for attempt in range(1, 11):
        try:
            pool.wait(timeout=5)
            with pool.connection() as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS notes (
                           id         BIGSERIAL PRIMARY KEY,
                           text       TEXT NOT NULL,
                           created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                       )"""
                )
            log.info("starting API (cors_origin=%s)", CORS_ORIGIN)
            break
        except Exception as exc:  # noqa: BLE001
            log.warning("database not ready (%s/10): %s", attempt, type(exc).__name__)
            if attempt == 10:
                log.error("cannot connect to the database")
                sys.exit(1)
            time.sleep(2)
    yield
    pool.close()


app = FastAPI(title="Notes API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    log.info("%s %s %s %dms", request.method, request.url.path, response.status_code,
             (time.time() - start) * 1000)
    return response


class NoteIn(BaseModel):
    text: str = Field(max_length=500)

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("text must be 1-500 characters")
        return v


class NoteOut(BaseModel):
    id: int
    text: str
    created_at: datetime


@app.get("/api/message")
def message():
    return {"message": APP_MESSAGE, "version": APP_VERSION}


@app.get("/api/notes", response_model=list[NoteOut])
def list_notes():
    with pool.connection() as conn:
        return conn.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id DESC LIMIT 100"
        ).fetchall()


@app.post("/api/notes", response_model=NoteOut, status_code=201)
def create_note(note: NoteIn):
    with pool.connection() as conn:
        return conn.execute(
            "INSERT INTO notes (text) VALUES (%s) RETURNING id, text, created_at", (note.text,)
        ).fetchone()


@app.get("/api/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT id, text, created_at FROM notes WHERE id = %s", (note_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(404, "note not found")
    return row


@app.put("/api/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note: NoteIn):
    with pool.connection() as conn:
        row = conn.execute(
            "UPDATE notes SET text = %s WHERE id = %s RETURNING id, text, created_at",
            (note.text, note_id),
        ).fetchone()
    if row is None:
        raise HTTPException(404, "note not found")
    return row


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with pool.connection() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    if cur.rowcount == 0:
        raise HTTPException(404, "note not found")
    return Response(status_code=204)


@app.get("/livez")
def livez():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    try:
        with pool.connection() as conn:
            conn.execute("SELECT 1")
    except Exception:  # noqa: BLE001
        raise HTTPException(503, "database unavailable")
    return {"status": "ok"}
