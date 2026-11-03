from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Note
from app.schemas import NoteCreate, NoteResponse


router = APIRouter(
    prefix="/api/notes",
    tags=["Notes"]
)


# GET /api/notes
# Retrieve all notes, newest first
@router.get("", response_model=list[NoteResponse])
def get_notes(db: Session = Depends(get_db)):

    notes = (
        db.query(Note)
        .order_by(Note.created_at.desc())
        .all()
    )

    return notes


# POST /api/notes
# Create a new note
@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED
)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db)
):

    new_note = Note(
        text=note_data.text
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note